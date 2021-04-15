# How to use these scripts
* ./benchmakrk.py --measure ./results
* ./benchmakrk.py --profile ./profile
* ./benchmark.py profile --profile_mode cpu_time --chromium_executable=./bin/Chromium.app

## benchmark.py
Use to execute different usage scenarios and measure their power use using powermetrics.

## powermetrics_compare.py
Parses and aggregates powermetrics results generated from benchmark.py --measure, generating a csv for each benchmark, and one for a high level summary.

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
