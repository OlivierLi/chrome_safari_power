#!/usr/bin/python3
import argparse
import os
import subprocess
import signal
import sys
import psutil
import time

import utils

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
    if scenario_config.browser in ["Chromium", "Chrome", "Canary", "Edge"]:
      subprocess.call(["open", "-a", browser_executable, "--args"] + ["--enable-benchmarking", "--disable-stack-profiler"] + scenario_config.extra_args)
    elif scenario_config.browser == "Safari":
      subprocess.call(["open", "-a", browser_executable])
      subprocess.call(["osascript", './driver_scripts/prep_safari.scpt'])
      subprocess.call(["open", "-a", browser_executable, "--args"] + scenario_config.extra_args)

  if scenario_config.background_script is not None:
    subprocess.call(["osascript", f'./driver_scripts/{background_script}.scpt'])

  driver_script_args = ["osascript", f'./driver_scripts/{scenario_config.driver_script}.scpt']

  process = subprocess.Popen(driver_script_args)
  time.sleep(2)
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

def GetAllPids(browser_process):
  pids = [browser_process.pid]
  children = browser_process.children(recursive=True)
  for child in children:
      pids.append(child.pid)

  return pids

def Profile(scenario_config, output_dir, dry_run=False):
  script_process = RunScenario(scenario_config)

  if scenario_config.browser != "Chromium":
    print("Only Chromium can be profiled!")
    exit(-1)

  browser_executable = utils.browsers_definition[scenario_config.browser]['process_name']
  processes = filter(lambda p: p.name() == browser_executable, psutil.process_iter())

  browser_process = None
  for process in processes:
    if not browser_process:
      browser_process = process
    else:
      print("Too many copies of the browser running, this is wrong")
      exit(-1)

  # Set up the environment for correct dtrace execution.
  my_env = os.environ.copy()
  my_env["DYLD_SHARED_REGION"] = "avoid"

  subprocess_to_pid = {}

  while script_process.poll() is None:

    time.sleep(0.100)
    print("Looking for child processes")

    # Watch for new processes and follow those too.
    # probe_def = f"mach_kernel::wakeup/pid == {pid}/ {{ @[ustack()] = count(); }}"
    probe_def = f"profile-1001/pid == {pid}/ {{ @[ustack()] = count(); }}"
    for pid in GetAllPids(browser_process):
      args = ['sudo', 'dtrace', '-p', f"{pid}", "-o", f"{output_dir}/{pid}.txt", '-n', 
             probe_def] 

      if pid not in subprocess_to_pid:
        if not dry_run:
          process = subprocess.Popen(args, env=my_env)
          subprocess_to_pid[pid] = process
        if dry_run:
          command = " ".join(args)
          subprocess_to_pid[pid] = command
          print(command)
 
  script_process.wait()
  KillBrowsers([scenario_config.browser])

class ScenarioConfig:
  def __init__(self, scenario_name, driver_script, browser, extra_args, background_script):
    self.scenario_name = scenario_name
    self.driver_script = driver_script
    self.browser = browser
    self.extra_args = extra_args
    self.background_script = background_script

def main():
  signal.signal(signal.SIGINT, SignalHandler)

  parser = argparse.ArgumentParser(description='Runs browser power benchmarks')
  parser.add_argument("output_dir", help="Output dir")
  parser.add_argument('--no-checks', dest='no_checks', action='store_true',
                    help="Invalid environment doesn't throw")
  parser.add_argument('--profile', dest='run_profile', action='store_true',
                    help="Run a profiling of the application for cpu use.")
  parser.add_argument('--measure', dest='run_measure', action='store_true',
                    help="Run measurments of the cpu use of the application.")
  parser.add_argument('--dry_run', dest='dry_run', action='store_true',
                    help="Do not actually profile run commands but print them out..")
  args = parser.parse_args()

  if args.run_measure and args.dry_run:
      print("Dry running measure is not implemented !")
      exit(-1)

  if args.run_profile and args.run_measure:
      print("Cannot measure and profile at the same time, choose one.")
      exit(-1)

  # Start by making sure that no browsers are running which would affect the test.
  KillBrowsers(utils.browsers_definition.keys())
  KillPowermetrics()
  os.makedirs(f"{args.output_dir}", exist_ok=True)

  # Verify that we run in an environment condusive to proper profiling or measurments.
  try:
    check_env = subprocess.run(['zsh', '-c', 'source ./check_env.sh && CheckEnv'], check=not args.no_checks, capture_output=True)
    print("WARNING:", check_env.stdout.decode('ascii'))
  except subprocess.CalledProcessError as e:
    print("ERROR:", e.stdout.decode('ascii'))
    return

  if args.run_measure:
    Record(ScenarioConfig("idle", "idle", None, None, None), args.output_dir)
    Record(ScenarioConfig("canary_idle_on_wiki_slack", "canary_idle_on_wiki", browser="Canary", extra_args=["--enable-features=LudicrousTimerSlack"], background_script=None), args.output_dir)
    Record(ScenarioConfig("canary_idle_on_wiki_slack_noslack", "canary_idle_on_wiki", browser="Canary", extra_args=["--disable-features=LudicrousTimerSlack"], background_script=None), args.output_dir)
    Record(ScenarioConfig("safari_idle_on_wiki", "safari_idle_on_wiki", browser="Safari", extra_args=None, background_script=None), args.output_dir)

  if args.run_profile:
    Profile(ScenarioConfig("chromium_idle_on_wiki", "chromium_idle_on_wiki", browser="Chromium", extra_args=[], background_script=None), args.output_dir, dry_run=args.dry_run)

if __name__== "__main__" :
  main()

