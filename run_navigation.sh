#! /bin/zsh

set -eu

POWERLOG=/Applications/Intel\ Power\ Gadget/Powerlog
OUTPUT_DIR=/Users/olivier/Documents/

# This script uses the open command which needs the path to the .app
CHROMIUM_APP=/Users/olivier/git/chromium/src/out/Baseline/Chromium.app

# Kill all browsers just to be sure.
killall -9 "Chromium" || true
killall -9 "Safari" || true

open $CHROMIUM_APP 
sleep 10 
$POWERLOG -resolution 5 -file $OUTPUT_DIR/chrome_navigation.csv -cmd osascript ./chrome_navigation.scpt;
# If kill fail abort. It means the browser quit itself.
killall "Chromium"

open -a Safari
sleep 10 
$POWERLOG -resolution 5 -file $OUTPUT_DIR/safari_navigation.csv -cmd osascript ./safari_navigation.scpt;
# If kill fail abort. It means the browser quit itself.
killall "Safari"
