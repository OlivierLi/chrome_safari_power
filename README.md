# How to use these scripts
* ./discharge.sh
* ./gadget_compare.py ./results/Chrome/any.csv ./results/Safari/any.csv

## compare.sh
Use to execute comparisons between two browsers. By default all scenarios are executed in a chain for all browsers but you can comment out any cases you don't care about.

## discharge_compare.py
Use to compare runs. The script should be provided with two csvs for a baseline and an experiment. This can be two versions of Chrome or Chrome and and another browser. The script will apply some safety checks before comparing and will warn the user if the experiment should be run again.

## pages/
This directory contains special webpages that can be loaded from disk in a navigator to verify certain behaviors.

## driver_scripts/
This directory contains scripts that can control the behaviour of Chrome or Safari to reproduce usage scenarios. The scripts will start the browsers if we want to include startup in the power capture. If not that can be done seperatly.

## check_env.sh
This file makes functions available to allow the other scripts to verify they are running in a sane environment for battery life testing.

# Signing your Chrome builds
Runnning the Chrome vs Chrome benchmarks require the use of signed builds. To do that you need to follow the following instructions:

1. Create a signing certificate in Xcode.
2. Find your code signing identity using `security find-identity -v -p codesigning`
3. Follow the chrome signing [instructions](https://source.chromium.org/chromium/chromium/src/+/master:chrome/installer/mac/signing/README.md)
4. Now you have a signed build!
