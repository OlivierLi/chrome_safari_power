import subprocess
import re
import os
import plistlib

browsers_definition = {
  "Chrome": {
    "executable": "Google Chrome",
    "identifier": "com.google.Chrome"
  },
  "Canary": {
    "executable": "Google Chrome Canary",
    "identifier": "com.google.Chrome.canary"
  },
  "Chromium": {
    "executable": "Chromium",
    "identifier": "org.chromium.Chromium"
  },
  "Edge": {
    "executable": "Microsoft Edge",
    "identifier": ""
  },
  "Safari": {
    "executable": "Safari",
    "identifier": "com.apple.Safari"
  }
}

def KillBrowsers(browser_list):
  for browser in browser_list:
    browser_executable = browsers_definition[browser]['executable']
    subprocess.call(["killall", "-9", browser_executable])

def Record(scenario_name, driver_script, browser, extra_args):
  browser_executable = browsers_definition[browser]['executable']

  with open("powermetrics.plist", "w") as f:
    powermetrics_process = subprocess.Popen(["sudo", "powermetrics", "-f", "plist", "--samplers", "all", "--show-responsible-pid", "--show-process-gpu", "--show-process-energy", "-i", "60000"], stdout=f, stdin=subprocess.PIPE)

  if (browser in ["Chrome", "Canary", "Edge"]):
    subprocess.call(["open", "-a", browser_executable, "--args"] + extra_args)
  elif browser == "Safari":
    subprocess.call(["open", "-a", browser_executable])
    subprocess.call(["osascript", './driver_scripts/prep_safari.scpt'])
    subprocess.call(["open", "-a", browser_executable, "--args"] + extra_args)

  discharge_process = subprocess.Popen(["./bin/Power.Mac.BatteryDischarge"])
  subprocess.call(["osascript", f'./driver_scripts/{driver_script}.scpt'])
  
  discharge_process.kill()
  subprocess.call(["sudo", "killall", "powermetrics"])
  KillBrowsers([browser])

  os.rename("./powermetrics.plist", f'./results/{scenario_name}_powermetrics.plist')
  os.rename("./battery_discharge.csv", f'./results/{scenario_name}_discharge.csv')

def main():
  KillBrowsers(["Chrome", "Canary", "Chromium", "Edge", "Safari"])
  subprocess.call(["killall", "Power.Mac.BatteryDischarge"])
  subprocess.call(["sudo", "killall", "powermetrics"])
  os.makedirs("./results", exist_ok=True)

  subprocess.run(['bash', '-c', 'source ./check_env.sh && CheckEnv'], check=False)
  
  #Record("canary_idle_on_wiki_slack", "canary_idle_on_wiki", "Canary", ["--enable-features=LudicrousTimerSlack"])
  #Record("canary_idle_on_wiki_noslack", "canary_idle_on_wiki", "Canary", ["--disable-features=LudicrousTimerSlack"])
  #Record("canary_idle_on_youtube_slack", "canary_idle_on_youtube", "Canary", ["--enable-features=LudicrousTimerSlack"])
  #Record("canary_idle_on_youtube_noslack", "canary_idle_on_youtube", "Canary", ["--disable-features=LudicrousTimerSlack"])
  #Record("safari_idle_on_wiki", "safari_idle_on_wiki", "Safari", [])
  Record("safari_idle_on_youtube", "safari_idle_on_youtube", "Safari", [])

  subprocess.call(["sudo", "killall", "powermetrics"])
main()