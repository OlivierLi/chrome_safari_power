#!/usr/bin/env python3
"""
Use this tool to compare two runs of intel power gadget and find the power use delta.

A "run" consists of N csv reports clearly numbered and located in the same directory.
"""

import pandas as pd
import sys
import os
import fnmatch
import shutil
import argparse

cumulative_energy_column_name = "Cumulative Processor Energy_0(mWh)"

def gather_files(dir_path):
    if not os.path.isdir(dir_path) or not os.path.exists(dir_path):
        print("Directory invalid:" + dir_path)
        sys.exit(-1)

    full_paths = []
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for filneame in filenames:
            full_paths.append(os.path.abspath(os.path.join(dirpath, filneame)))

    # Ignore anything that's not a csv
    csvs = [ file_path for file_path in full_paths if file_path.endswith(".csv") ]

    return csvs

def load_dir(dir_path):

    agg_data = pd.DataFrame({cumulative_energy_column_name : []})

    for csv in gather_files(dir_path):
        df = pd.read_csv(csv, engine="python", header=0, skipfooter=15, na_values = [''])
        cumulative_package_energy = df[cumulative_energy_column_name].max()

        # Not the most efficient thing. Change to concat if this is getting slow.
        agg_data = agg_data.append({cumulative_energy_column_name: cumulative_package_energy}, ignore_index = True)
   
    return clean(agg_data)

def get_sign(diff):
    if diff > 0:
        return '+'
    else:
        # Minus sign added by str()
        return ''

# Check data for major outliers and remove them.
def clean(df):

    # If ever more than one column is included then the means have to be calculated before pruning and z score needs to be done per column
    # https://stackoverflow.com/a/24762240
    assert(df.shape[1] == 1)

    df['z_score'] = df.apply(lambda x: (x - x.mean())/x.std())
    df = df[abs(df['z_score']) < 3]

    return df.drop(columns=['z_score'])    


def compare(baseline, experiment):
    assert(baseline.columns.equals(experiment.columns))

    # In relation to the size of the baseline dataset.
    acceptable_experiment_size_difference = 0.1
    if abs(baseline.shape[0] - experiment.shape[0]) / baseline.shape[0] > 0.1:
        print("The two datasets have mismatched sizes, rerun experiments to get comparable data")
        return

    for column in baseline.columns:
        baseline_value = baseline[column].mean()
        experiment_value = experiment[column].mean() 
        diff = experiment_value - baseline_value 
        percent_change = 100*diff/baseline_value 

        print("Baseline avg {}: {:0.2f}".format(column, baseline_value)) 
        print("Baseline max {}: {:0.2f}".format(column, baseline[column].max())) 
        print("Baseline min {}: {:0.2f}".format(column, baseline[column].min())) 

        print("Experiment avg {}: {:0.2f}".format(column, experiment_value)) 
        print("Experiment max {}: {:0.2f}".format(column, experiment[column].max()))
        print("Experiment min {}: {:0.2f}".format(column, experiment[column].min()))

        print("Change in avg {}: {}{:0.2f} ({:0.2f}%)".format(column, get_sign(diff), diff, percent_change)) 

def main():
    parser = argparse.ArgumentParser(description="Use gadget_compare to compare two runs of intel power gadget.")
    parser.add_argument("baseline_dir", help="The directory containing reports for the baseline measurments.")
    parser.add_argument("experiment_dir", help="The directory containing reports for the measurments of the modified code.")
    args = vars(parser.parse_args())

    baseline = load_dir(args["baseline_dir"])
    experiment = load_dir(args["experiment_dir"])

    compare(baseline, experiment)


if __name__ == "__main__":
    main()
