#!/usr/bin/env python3
"""
Use this tool to compare results from discharge.sh.
"""

import pandas as pd
import sys
import os
import fnmatch
import shutil
import argparse
import pathlib

def read_csv(dir_path):
    df = pd.read_csv(dir_path, engine="python", header=0, skipfooter=0, na_values = [''])
    df = clean(df[[' Power.Mac.BatteryDischarge']])
    return df

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

    df = df.assign(z_score=df.apply(lambda x: (x - x.mean())/x.std()))
    df = df[abs(df['z_score']) < 3]

    cleaned = df.drop(columns=['z_score'])    

    return cleaned

def print_result(name, df, column, ):
    print(name+":"+column)
    print("avg : {:0.2f}".format(df[column].mean())) 
    print("max : {:0.2f}".format(df[column].max())) 
    print("min : {:0.2f}".format(df[column].min())) 

def compare(baseline, baseline_name, experiment, experiment_name):
    assert(baseline.columns.equals(experiment.columns))

    # In relation to the size of the baseline dataset.
    acceptable_experiment_size_difference = 0.1
    if abs(baseline.shape[0] - experiment.shape[0]) / baseline.shape[0] > 0.1:
        print("The two datasets have mismatched sizes (after cleaning), rerun experiments to get comparable data")
        # return

    for column in baseline.columns:
        print("---")
        print_result(baseline_name, baseline, column)
        print("---")
        print_result(experiment_name, experiment, column)
        print("---")

        baseline_value = baseline[column].mean()
        experiment_value = experiment[column].mean() 
        diff = experiment_value - baseline_value 
        percent_change = 100*diff/baseline_value 
        print("Change in avg {}: {}{:0.2f} ({:0.2f}%)".format(column, get_sign(diff), diff, percent_change)) 
        print("---")

def get_name(path):
    return os.path.basename(os.path.dirname(path)) + "-" + pathlib.PurePath(path).stem 

def main():
    parser = argparse.ArgumentParser(description="Use gadget_compare to compare results from discharge.sh.")
    parser.add_argument("baseline_csv", help="The report containing the baseline measurments.")
    parser.add_argument("experiment_csv", help="The report containing the measurments of the experiment.")
    args = vars(parser.parse_args())

    baseline = read_csv(args["baseline_csv"])
    experiment = read_csv(args["experiment_csv"])
    compare(baseline, get_name(args["baseline_csv"]), experiment, get_name(args["experiment_csv"]), )

if __name__ == "__main__":
    main()
