#! /bin/zsh

set -eu

# Get the functions
source ./functions.sh

CheckEnv

# Parameters
SITES="polygon.com"
RUN="IncreasedMemory2GB"
OUTPUT_DIR=/Users/olivier/Documents/
mkdir -p $OUTPUT_DIR

# Binaries
POWERLOG=/Applications/Intel\ Power\ Gadget/Powerlog
BASELINE_BIN=~/git/chromium/src/out/Baseline/Chromium.app/Contents/MacOS/Chromium 
EXPERIMENT_BIN=~/git/chromium/src/out/Release/Chromium.app/Contents/MacOS/Chromium 

for i in $(seq 1 60); do 
  echo $i;
  $POWERLOG -resolution 10 -file $OUTPUT_DIR/Baseline/power.$i.csv -cmd $BASELINE_BIN $SITES;
  $POWERLOG -resolution 10 -file $OUTPUT_DIR/$RUN/power.$i.csv -cmd $EXPERIMENT_BIN $SITES;
done
