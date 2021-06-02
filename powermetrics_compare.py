#!/usr/bin/python3
import argparse
import plistlib
import csv
import pandas as pd
from scipy import stats
import numpy as np

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
  scenario_summary = {}
  for scenario in results:
    scenario_result = results[scenario].drop(0)
    scenario_result = results[scenario].drop(0)

    nanoseconds_to_seconds = 1000000000.0
    scenario_result['elapsed_s'] = scenario_result['elapsed_ns'] / nanoseconds_to_seconds
    scenario_result[rate_columns] = scenario_result[rate_columns].mul(scenario_result['elapsed_s'], axis=0)
    
    # Replace NaN by 0.
    scenario_result['charge_delta'] = scenario_result['charge_delta'].fillna(0)

    # Remove all rows that has an outlier value for one of 'elapsed_s', 'charge_delta' or 'package_joules'.
    # An outlier is a value with |z-score| > 3.
    print(scenario_result["charge_delta"].std())
    print(scenario_result["charge_delta"].mean())
    scenario_result = scenario_result[(np.abs(stats.zscore(scenario_result[['elapsed_s', 'charge_delta', 'package_joules']])) < 3).all(axis=1)]

    # Positive "discharge" is impossible. Remove.
    scenario_result = scenario_result.loc[scenario_result['charge_delta'] < 0]

    # Remove samples for which the battery could not be acquired.
    nan_value = float("NaN")
    scenario_result.replace("", nan_value, inplace=True)
    scenario_result.dropna(subset = ["battery_capacity"], inplace=True)

    if scenario_result.empty:
      print(scenario + " is empty after NaN and outlier filtering. Check your file!")
      continue

    # Sum all rows for |sum_columns|.
    scenario_summary[scenario] = scenario_result[sum_columns].sum()
    scenario_summary[scenario]['elapsed_s'] = scenario_result['elapsed_s'].sum()
    scenario_summary[scenario]['total_discharge'] = scenario_result['charge_remaining'].iloc[0] - scenario_result['charge_remaining'].iloc[-1]
    scenario_summary[scenario]['average_discharge'] = scenario_result['charge_delta'].mean()

  summary_results = pd.DataFrame.from_dict(scenario_summary, orient='index')
  summary_results[sum_columns] = summary_results[sum_columns].div(summary_results['elapsed_s'], axis=0)

  print(summary_results)
  summary_results.to_csv(filename)

def main():
  parser = argparse.ArgumentParser(description='Parses and aggregates powermetrics results')
  parser.add_argument("data_dir", help="Data dir")
  args = parser.parse_args()

  scenarios = [
    {"name": "idle"},
    # {"name": "canary_idle_on_youtube_slack", "browser": "Canary"},
    # {"name": "canary_idle_on_youtube_noslack", "browser": "Canary"},
    # {"name": "safari_idle_on_youtube", "browser": "Safari"},
    # {"name": "canary_idle_on_wiki_slack", "browser": "Canary"},
    # {"name": "canary_idle_on_wiki_noslack", "browser": "Canary"},

    {"name": "chrome_navigation", "browser": "Chrome"},
    {"name": "safari_navigation", "browser": "Safari"},
    {"name": "chrome_idle_on_wiki", "browser": "Chrome"},
    {"name": "safari_idle_on_wiki", "browser": "Safari"},
    {"name": "chrome_idle_on_wiki_hidden", "browser": "Chrome"},
    {"name": "safari_idle_on_wiki_hidden", "browser": "Safari"},
    {"name": "chrome_idle_on_youtube", "browser": "Chrome"},
    {"name": "safari_idle_on_youtube", "browser": "Safari"},
    {"name": "chrome_zero_window", "browser": "Chrome"},
    {"name": "safari_zero_window", "browser": "Safari"}
  ]
  results = {}
  for scenario in scenarios:
    browser = None
    if "browser" in scenario:
      browser = scenario["browser"]
    columns = [
      "elapsed_ns",
      "battery_capacity",
      "charge_remaining",
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
    print("\n Reading " + scenario["name"] + "...")
    try:
      samples = pd.DataFrame.from_records(ReadResults(scenario["name"], browser), columns=columns)
    except:
      print(scenario["name"] + " cannot be read. Check file!")
      continue

    if samples.empty:
      print(scenario["name"] + " is empty. Check file!")
      continue

    samples.to_csv(f"{args.data_dir}/{scenario['name']}.csv")
    results[scenario["name"]] = samples
  if results:
    Summary(results, f"{args.data_dir}/summary.csv")

if __name__== "__main__" :
  main()
