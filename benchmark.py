#!/usr/bin/python3
import argparse
import os
import subprocess
import signal
import sys

import utils

def KillBrowsers(browser_list):
  for browser in browser_list:
    browser_executable = utils.browsers_definition[browser]['executable']
    subprocess.call(["killall", "-9", browser_executable])

def KillPowermetrics():
  # killall because sudo required
  print("Possibly enter password for killing power_metrics:")
  subprocess.call(["sudo", "killall", "powermetrics"])

def SignalHandler(sig, frame):
  KillPowermetrics()
  sys.exit(0)

def Record(scenario_name, driver_script, output_dir, browser=None, extra_args=[], background_script=None):

  with open(f'./{output_dir}/{scenario_name}_powermetrics.plist', "w") as f:
    print("Possibly enter password for running power_metrics:")
    powermetrics_process = subprocess.Popen(["sudo", "powermetrics", "-f", "plist", "--samplers", "all", "--show-responsible-pid", "--show-process-gpu", "--show-process-energy", "-i", "60000"], stdout=f, stdin=subprocess.PIPE)

  if browser is not None:
    browser_executable = utils.browsers_definition[browser]['executable']
    if browser in ["Chrome", "Canary", "Edge"]:
      subprocess.call(["open", "-a", browser_executable, "--args"] + ["--enable-benchmarking", "--disable-stack-profiler"] + extra_args)
    elif browser == "Safari":
      subprocess.call(["open", "-a", browser_executable])
      subprocess.call(["osascript", './driver_scripts/prep_safari.scpt'])
      subprocess.call(["open", "-a", browser_executable, "--args"] + extra_args)

  if background_script is not None:
    subprocess.call(["osascript", f'./driver_scripts/{background_script}.scpt'])

  subprocess.call(["osascript", f'./driver_scripts/{driver_script}.scpt'])
  
  KillPowermetrics()
  if browser is not None:
    KillBrowsers([browser])

def main():
  parser = argparse.ArgumentParser(description='Runs browser power benchmarks')
  parser.add_argument('--no-checks', dest='no_checks', action='store_true',
                    help="Invalid environment doesn't throw")
  parser.add_argument("output_dir",
                    help="Output dir")
  args = parser.parse_args()

  signal.signal(signal.SIGINT, SignalHandler)
  
  KillBrowsers(utils.browsers_definition.keys())
  KillPowermetrics()
  os.makedirs(f"{args.output_dir}", exist_ok=True)

  try:
    check_env = subprocess.run(['zsh', '-c', 'source ./check_env.sh && CheckEnv'], check=not args.no_checks, capture_output=True)
    print("WARNING:", check_env.stdout.decode('ascii'))
  except subprocess.CalledProcessError as e:
    print("ERROR:", e.stdout.decode('ascii'))
    return

  Record("canary_idle_on_wiki_slack", "canary_idle_on_wiki", args.output_dir, browser="Canary", extra_args=["--enable-features=LudicrousTimerSlack"])
  Record("canary_idle_on_wiki_noslack", "canary_idle_on_wiki", args.output_dir, browser="Canary", extra_args=["--disable-features=LudicrousTimerSlack"])
  Record("canary_idle_on_youtube_slack", "canary_idle_on_youtube", args.output_dir, browser="Canary", extra_args=["--enable-features=LudicrousTimerSlack"])
  Record("canary_idle_on_youtube_noslack", "canary_idle_on_youtube", args.output_dir, browser="Canary", extra_args=["--disable-features=LudicrousTimerSlack"])
  Record("safari_idle_on_wiki", "safari_idle_on_wiki", args.output_dir, browser="Safari")
  Record("safari_idle_on_youtube", "safari_idle_on_youtube", args.output_dir, browser="Safari")
  Record("idle", "idle", args.output_dir)

if __name__== "__main__" :
  main()

