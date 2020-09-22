# Chrome and Safari power use scripts
This set of scripts allows the comparison of power use of Chrome and Safari.

## gadget_compare.py
Use to compare runs of intel power gadget. The script should be provided with two directories that contain the csv reports from PowerMonitor for a baseline and an experiment. This can be two versions of Chrome or Chrome and Safari. The script will apply some safety checks before comparing and will warn the user if the experiment should be run again.
