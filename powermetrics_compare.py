#!/usr/bin/python3
import argparse
import plistlib
import csv
import pandas as pd

import utils

def FindTask(tasks, process_name):
  for task in tasks:
    if task['name'] == process_name:
      return task
  return None

def FindChildrenTask(tasks, pid):
  children = []
  for task in tasks:
    if task['responsible_pid'] == pid:
      children.append(task)
  return children

def SumTaskMetric(tasks, key):
  value = 0
  for task in tasks:
    if key in task:
      value += task[key]
  return value

def ReadResults(scenario_name, browser):
  with open(f"results/{scenario_name}_powermetrics.plist", "r") as fp:
    data = fp.read().split('\0')
    browser_pid = None
    for chunk in data:
      if chunk == "":
        continue
      info = plistlib.loads(str.encode(chunk))
      tasks = info['tasks']
      sample={}
      sample["elapsed_ns"]= info["elapsed_ns"]
      if "battery" in info:
        sample["battery_capacity"]= info["battery"]["capacity"]
        sample["charge_remaining"]= info["battery"]["charge_remaining"]
        sample["charge_delta"]= info["battery"]["charge_delta"]
      sample["backlight"]= info["backlight"]["value"]
      sample["package_joules"]= info["processor"]["package_joules"]

      if browser is not None and browser_pid is None:
        browser_executable = utils.browsers_definition[browser]['executable']
        browser_task = FindTask(tasks, browser_executable)
        if browser_task is not None:
          browser_pid = browser_task["pid"]
      if browser_pid is not None:
        responsible_tasks = FindChildrenTask(tasks, browser_pid)
        
        task_keys = [
          "energy_impact", 
          "pageins",
          "intr_wakeups", 
          "idle_wakeups", 
          "cputime_ns", 
          "gputime_ns", 
          "bytes_received", 
          "bytes_sent", 
          "packets_received", 
          "packets_sent"
        ]
        for key in task_keys:
          sample[key] = SumTaskMetric(responsible_tasks, key)
        for task in responsible_tasks:
          if 'timer_wakeups' in task:
            for wakeup in task['timer_wakeups']:
              key = f"wakeups_{wakeup['interval_ns']}"
              sample[key] = sample.get(key, 0) + wakeup['wakeups'] 
      yield sample


def Summary(results, filename):
  rate_columns = [
    "backlight"
  ]
  sum_columns = [
    "charge_delta", 
    "package_joules", 
    "energy_impact", 
    "pageins",
    "intr_wakeups", 
    "idle_wakeups", 
    "cputime_ns", 
    "gputime_ns", 
    "packets_received", 
    "packets_sent",
    "wakeups_2000000",
    "wakeups_5000000"
  ]
  sums = {}
  for scenario in results:
    scenario_result = results[scenario].drop(0)
    nanoseconds_to_seconds = 1000000000.0
    scenario_result['elapsed_s'] = scenario_result['elapsed_ns'] / nanoseconds_to_seconds

    scenario_result[rate_columns] = scenario_result[rate_columns].mul(scenario_result['elapsed_s'], axis=0)
    sums[scenario] = scenario_result[sum_columns].sum()
    sums[scenario]['elapsed_s'] = scenario_result['elapsed_s'].sum()
  summary_results = pd.DataFrame.from_dict(sums, orient='index')
  summary_results = summary_results.div(summary_results['elapsed_s'], axis=0)[sum_columns]
  print(summary_results)
  summary_results.to_csv(filename)

def main():
  parser = argparse.ArgumentParser(description='Parses and aggregates powermetrics results')
  parser.add_argument("data_dir", help="Data dir")
  args = parser.parse_args()

  scenarios = [
    {"name": "idle"},
    {"name": "canary_idle_on_youtube_slack", "browser": "Canary"},
    {"name": "canary_idle_on_youtube_noslack", "browser": "Canary"},
    {"name": "canary_idle_on_wiki_slack", "browser": "Canary"},
    {"name": "canary_idle_on_wiki_noslack", "browser": "Canary"},
    {"name": "safari_idle_on_youtube", "browser": "Safari"},
    {"name": "safari_idle_on_wiki", "browser": "Safari"}
  ]
  results = {}
  for scenario in scenarios:
    browser = None
    if "browser" in scenario:
      browser = scenario["browser"]
    columns = [
      "elapsed_ns",
      "charge_delta", 
      "backlight",
      "package_joules", 
      "energy_impact", 
      "pageins",
      "intr_wakeups", 
      "idle_wakeups", 
      "cputime_ns", 
      "gputime_ns", 
      "packets_received", 
      "packets_sent",
      "wakeups_2000000",
      "wakeups_5000000"
    ]
    samples = pd.DataFrame.from_records(ReadResults(scenario["name"], browser), columns=columns)
    samples.to_csv(f"{args.data_dir}/{scenario}.csv")
    print(scenario, samples)
    results[scenario["name"]] = samples
  Summary(results, f"{args.data_dir}/summary.csv")

if __name__== "__main__" :
  main()
