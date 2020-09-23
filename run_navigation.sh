#! /bin/zsh

set -eu

# Get the functions
source ./functions.sh

CheckEnv

POWERLOG=/Applications/Intel\ Power\ Gadget/Powerlog
OUTPUT_DIR=/Users/olivier/Documents/TripleNavigations/
mkdir -p $OUTPUT_DIR

# This script uses the open command which needs the path to the .app
CHROMIUM_APP=/Users/olivier/git/chromium/src/out/Baseline/Chromium.app

# Kill all browsers just to be sure.
killall -9 "Chromium" || true
killall -9 "Safari" || true

for i in $(seq 1 60); do 
  echo $i;

  open $CHROMIUM_APP 
  sleep 10 
  $POWERLOG -resolution 5 -file $OUTPUT_DIR/chrome_navigation.$i.csv -cmd osascript ./chrome_navigation.scpt;
  # If kill fail abort. It means the browser quit itself.
  killall "Chromium"

  # Safari needs this housekeeping to clear all open tabs otherwise
  # they get restored.
  open -a Safari
  osascript ./prep_safari.scpt;
  open -a Safari

  sleep 10 
  $POWERLOG -resolution 5 -file $OUTPUT_DIR/safari_navigation.$i.csv -cmd osascript ./safari_navigation.scpt;
  # If kill fail abort. It means the browser quit itself.
  killall "Safari"

done
