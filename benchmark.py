#!/usr/bin/python3
import argparse
import os
import subprocess
import signal
import sys
import psutil
import time

import utils
import generate_scripts

def KillBrowsers(browser_list):
  for browser in browser_list:
    process_name = utils.browsers_definition[browser]['process_name']
    subprocess.call(["killall", "-9", process_name])

def KillPowermetrics():
  # killall because sudo required
  print("Possibly enter password for killing power_metrics/dtrace:")
  subprocess.call(["sudo", "killall", "-9", "powermetrics"])
  subprocess.call(["sudo", "killall", "-9", "dtrace"])

def SignalHandler(sig, frame):
  KillPowermetrics()
  sys.exit(0)

def RunScenario(scenario_config):

  if scenario_config.extra_args is None:
    scenario_config.extra_args = []

  if scenario_config.browser is not None:
    browser_executable = utils.browsers_definition[scenario_config.browser]['executable']
    if scenario_config.browser in ["Chrome", "Canary", "Edge"]:
      subprocess.call(["open", "-a", browser_executable, "--args"] + ["--enable-benchmarking", "--disable-stack-profiler"] + scenario_config.extra_args)
    elif scenario_config.browser == "Chromium":
      subprocess.Popen([browser_executable, "--enable-benchmarking", "--disable-stack-profiler"] + scenario_config.extra_args)
    elif scenario_config.browser == "Safari":
      subprocess.call(["open", "-a", browser_executable])
      subprocess.call(["osascript", './driver_scripts/prep_safari.scpt'])
      subprocess.call(["open", "-a", browser_executable, "--args"] + scenario_config.extra_args)

  # Wait for the browser to be started before continuing on.
  if scenario_config.browser:
    browser_process_name = utils.browsers_definition[scenario_config.browser]['process_name']
    while not FindBrowserProcess(browser_process_name):
      time.sleep(0.100)
      print(f"Waiting for {browser_process_name} to start")

  # Wait for browser to be receptive to applescript commands which is not automatic if it was not started with "open".
  # TODO: Actually try and ping pong AppleScript commands instead of just having a random wait.
  time.sleep(5)

  if scenario_config.background_script is not None:
    subprocess.call(["osascript", f'./driver_scripts/{background_script}.scpt'])

  driver_script_args = ["osascript", f'./driver_scripts/{scenario_config.driver_script}.scpt']
  process = subprocess.Popen(driver_script_args)

  return process


def Record(scenario_config, output_dir):
  with open(f'./{output_dir}/{scenario_config.scenario_name}_powermetrics.plist', "w") as f:
    print("Possibly enter password for running power_metrics:")
    powermetrics_process = subprocess.Popen(["sudo", "powermetrics", "-f", "plist", "--samplers", "all", "--show-responsible-pid", "--show-process-gpu", "--show-process-energy", "-i", "60000"], stdout=f, stdin=subprocess.PIPE)

  scenario_process = RunScenario(scenario_config)
  scenario_process.wait()
  
  KillPowermetrics()

  if scenario_config.browser is not None:
    KillBrowsers([scenario_config.browser])


def FindBrowserProcess(process_name):
  processes = filter(lambda p: p.name() == process_name, psutil.process_iter())
  browser_process = None

  for process in processes:
    if not browser_process:
      browser_process = process
    else:
      print("Too many copies of the browser running, this is wrong")
      exit(-1)
  
  return browser_process


def GetAllPids(browser_process):
  pids = [browser_process.pid]
  try:
    children = browser_process.children(recursive=True)
  except psutil.NoSuchProcess:
    return []

  for child in children:
      pids.append(child.pid)

  return pids


def Profile(scenario_config, output_dir, dry_run, profile_mode):
  if scenario_config.browser != "Chromium":
    print("Only Chromium can be profiled!")
    exit(-1)

  script_process = RunScenario(scenario_config)
  browser_process = FindBrowserProcess(utils.browsers_definition[scenario_config.browser]['process_name'])

  # Set up the environment for correct dtrace execution.
  my_env = os.environ.copy()
  my_env["DYLD_SHARED_REGION"] = "avoid"

  pid_to_subprocess = {}

  with open(f'./dtrace_log.txt', "w") as dtrace_log:
    # Keep looking for child processes as long as the scenario is running.
    while script_process.poll() is None:

      # Let some time pass to limit the overhead of this script.
      time.sleep(0.100)
      print("Looking for child processes")

      # Watch for new processes and follow those too.
      for pid in GetAllPids(browser_process):
        if profile_mode == "wakeups":
          probe_def = f"mach_kernel::wakeup/pid == {pid}/ {{ @[ustack()] = count(); }}"
        else:
          probe_def = f"profile-1001/pid == {pid}/ {{ @[ustack()] = count(); }}"

        args = ['sudo', 'dtrace', '-p', f"{pid}", "-o", f"{output_dir}/{pid}.txt", '-n', 
               probe_def] 

        if pid not in pid_to_subprocess:
          print(f"Found new child!:{pid}")
          if not dry_run:
            process = subprocess.Popen(args, env=my_env, stdout=dtrace_log, stderr=dtrace_log)
            pid_to_subprocess[pid] = process
          if dry_run:
            command = " ".join(args)
            pid_to_subprocess[pid] = command
            print(command)
 
  script_process.wait()
  KillBrowsers([scenario_config.browser])

  for pid, dtrace_process in pid_to_subprocess.items():
      time.sleep(0.100)
      print(f"Waiting for dtrace hooked on {pid} to exit")
      dtrace_process.wait()

class ScenarioConfig:
  def __init__(self, scenario_name, driver_script, browser, extra_args, background_script):
    self.scenario_name = scenario_name
    self.driver_script = driver_script
    self.browser = browser
    self.extra_args = extra_args
    self.background_script = background_script

    if browser == "Chromium" and "executable" not in utils.browsers_definition["Chromium"].keys():
        print("Cannot run a Chromium scenario without the executable defined")
        exit(-1)

def main():
  signal.signal(signal.SIGINT, SignalHandler)

  parser = argparse.ArgumentParser(description='Runs browser power benchmarks')
  parser.add_argument("output_dir", help="Output dir")
  parser.add_argument('--no-checks', dest='no_checks', action='store_true',
                    help="Invalid environment doesn't throw")
  parser.add_argument('--measure', dest='run_measure', action='store_true',
                    help="Run measurments of the cpu use of the application.")

  # Profile related arguments
  parser.add_argument('--profile_mode', dest='profile_mode', action='store', choices=["wakeups", "cpu_time"],
          help="Run a profiling of the application in one of two modes: wakeups, cpu_time.")
  parser.add_argument('--dry_run', dest='dry_run', action='store_true',
                    help="Do not actually profile run commands but print them out.")
  parser.add_argument('--chromium_executable', dest='chromium_executable', action='store',
                    help="Absolute path to a locally built Chromium binary.")

  args = parser.parse_args()

  if args.run_measure and args.dry_run:
      print("Dry running measure is not implemented !")
      exit(-1)

  if args.profile_mode and args.run_measure:
      print("Cannot measure and profile at the same time, choose one.")
      exit(-1)

  if args.chromium_executable:
      utils.browsers_definition["Chromium"]["executable"] = args.chromium_executable

  # Start by making sure that no browsers are running which would affect the test.
  KillBrowsers(utils.browsers_definition.keys())
  KillPowermetrics()
  os.makedirs(f"{args.output_dir}", exist_ok=True)

  # Generate the runner scripts
  generate_scripts.generate_all()

  # Verify that we run in an environment condusive to proper profiling or measurments.
  try:
    check_env = subprocess.run(['zsh', '-c', 'source ./check_env.sh && CheckEnv'], check=not args.no_checks, capture_output=True)
    print("WARNING:", check_env.stdout.decode('ascii'))
  except subprocess.CalledProcessError as e:
    print("ERROR:", e.stdout.decode('ascii'))
    return

  # Start by making sure that no browsers are running which would affect the test.
  KillBrowsers(utils.browsers_definition.keys())
  KillPowermetrics()
  os.makedirs(f"{args.output_dir}", exist_ok=True)

  if args.run_measure:
    # Record(ScenarioConfig("idle", "idle", None, None, None), args.output_dir)
    Record(ScenarioConfig("chrome_navigation", "chrome_navigation", browser="Chrome", extra_args=["--guest"], background_script=None), args.output_dir)
    Record(ScenarioConfig("safari_navigation", "safari_navigation", browser="Safari", extra_args=None, background_script=None), args.output_dir)
    # Record(ScenarioConfig("chrome_idle_on_wiki", "chrome_idle_on_wiki", browser="Chrome", extra_args=["--guest"], background_script=None), args.output_dir)
    # Record(ScenarioConfig("safari_idle_on_wiki", "safari_idle_on_wiki", browser="Safari", extra_args=None, background_script=None), args.output_dir)
    # Record(ScenarioConfig("chrome_idle_on_wiki_hidden", "chrome_idle_on_wiki_hidden", browser="Chrome", extra_args=["--guest"], background_script=None), args.output_dir)
    # Record(ScenarioConfig("safari_idle_on_wiki_hidden", "safari_idle_on_wiki_hidden", browser="Safari", extra_args=None, background_script=None), args.output_dir)
    # Record(ScenarioConfig("chrome_zero_window", "chrome_zero_window", browser="Chrome", extra_args=["--guest"], background_script=None), args.output_dir)
    # Record(ScenarioConfig("safari_zero_window", "safari_zero_window", browser="Safari", extra_args=None, background_script=None), args.output_dir)
    # Record(ScenarioConfig("chrome_idle_on_youtube", "chrome_idle_on_youtube", browser="Chrome", extra_args=["--guest"], background_script=None), args.output_dir)
    # Record(ScenarioConfig("safari_idle_on_youtube", "safari_idle_on_youtube", browser="Safari", extra_args=None, background_script=None), args.output_dir)

  if args.profile_mode:
    Profile(ScenarioConfig("chromium_navigation", "chromium_navigation", browser="Chromium", extra_args=[], background_script=None), args.output_dir, dry_run=args.dry_run, profile_mode=args.profile_mode)

if __name__== "__main__" :
  main()

