# How to use these scripts
* ./compare_chrome_safari.sh
* ./gadget_compare.py {chrome_result_dir} {safari_result_dir}

## gadget_compare.py
Use to compare runs of intel power gadget. The script should be provided with two directories that contain the csv reports from PowerMonitor for a baseline and an experiment. This can be two versions of Chrome or Chrome and Safari. The script will apply some safety checks before comparing and will warn the user if the experiment should be run again.

## compare_chrome_safari.sh
Use to execute 60 runs of comparisons between Chrome and Safari. By default the single navigation scenario is executed by you can look at the impl to know how to switch this up.

## compare_chromes.sh
Use to execute 60 runs of comparisons between two versions of Chrome. By default the idle on page scenario is executed by you can look at the impl to know how to switch this up.

## pages/
This directory contains special webpages that can be loaded from disk in a navigator to verify certain behaviors.

## driver_scripts/
This directory contains scripts that can control the behaviour of Chrome or Safari to reproduce usage scenarios. The scripts are not responsible for starting the application. This should be done seperatly.

## check_env.sh
This file makes functions available to allow the other scripts to verify they are running in a sane environment for battery life testing.
