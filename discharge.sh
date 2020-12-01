#! /bin/zsh

set -eux

# Get the functions
source check_env.sh
source ./compare.sh

CheckEnv

# Local paths
BIN=/Users/olivier/Library/Developer/Xcode/DerivedData/Power.Mac.BatteryDischarge-frtspoojsdrdsycbpuzpwyqlczdp/Build/Products/Debug/Power.Mac.BatteryDischarge

# Kill everything just to be sure.
function KillALL(){
  killall -9 "Chromium" || true
  killall -9 "Google Chrome" || true
  killall -9 "Safari" || true

  # Make sure we're not already recording
  killall Power.Mac.BatteryDischarge || true
}

function Record(){
  KillALL

  # Start the collection of Power.Mac.BatteryDischarge
  $BIN&

  # Run the scenario.
  OUTPUT_DIR=./results
  RecordPower $1  $1 ./driver_scripts/${1}_setup_idle_on_site.scpt "Experiment" ""

  KillALL

  # Rename the results and save.
  mv battery_discharge.csv ./results/$1/$2.csv
}

SCENARIO="idle_on_site"
Record "Chrome" $SCENARIO
Record "Safari" $SCENARIO

