#! /bin/zsh

set -eux

POWERLOG=/Applications/Intel\ Power\ Gadget/Powerlog
OUTPUT_DIR=/Users/olivier/Documents/

BASELINE_BIN=~/git/chromium/src/out/Baseline/Chromium.app/Contents/MacOS/Chromium 

killall -9 "Google Chrome" || true
killall -9 "Safari" || true

open -a "Google Chrome"
sleep 10 
$POWERLOG -resolution 5 -file $OUTPUT_DIR/chrome_navigation.csv -cmd osascript ./chrome_navigation.scpt;
killall "Google Chrome" || true

killall "Safari" || true
open -a Safari
sleep 10 
$POWERLOG -resolution 5 -file $OUTPUT_DIR/safari_navigation.csv -cmd osascript ./safari_navigation.scpt;
killall "Safari" || true
