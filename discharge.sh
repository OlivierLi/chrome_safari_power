#! /bin/zsh

set -eux

# Get the functions
source check_env.sh
source ./compare.sh

#CheckEnv

# Local paths
BIN=/Users/olivier/Library/Developer/Xcode/DerivedData/Power.Mac.BatteryDischarge-frtspoojsdrdsycbpuzpwyqlczdp/Build/Products/Debug/Power.Mac.BatteryDischarge

# Kill everything just to be sure.
function KillALL(){
  killall -9 "Chromium" || true
  killall -9 "Google Chrome" || true
  killall -9 "Safari" || true
  killall -9 "Microsoft Edge" || true

  # Make sure we're not already recording
  killall Power.Mac.BatteryDischarge || true
}

function Record(){
  KillALL

  # Start the collection of Power.Mac.BatteryDischarge
  $BIN&

  # Run the scenario.
  OUTPUT_DIR=./results
  RecordPower $1 $1 ./driver_scripts/${1}_${2}.scpt "Experiment" "" $4

  KillALL

  # Rename the results and save.
  mv battery_discharge.csv ./results/$1/$3.csv
}

./generate_scripts.py

SCENARIO="idle_on_wiki"
Record "Chrome" $SCENARIO $SCENARIO "NONE"
Record "Safari" $SCENARIO $SCENARIO "NONE"
Record "Edge" $SCENARIO $SCENARIO "NONE"

SCENARIO="navigation"
Record "Chrome" $SCENARIO $SCENARIO "NONE"
Record "Safari" $SCENARIO $SCENARIO "NONE"
Record "Edge" $SCENARIO $SCENARIO "NONE"

SCENARIO="navigation"
Record "Chrome" $SCENARIO ${SCENARIO}_with_background "./driver_scripts/chrome_open_background.scpt"
Record "Safari" $SCENARIO ${SCENARIO}_with_background "./driver_scripts/safari_open_background.scpt"
Record "Chrome" $SCENARIO ${SCENARIO}_with_background "./driver_scripts/edge_open_background.scpt"

SCENARIO="Scroll"
Record "Chrome" $SCENARIO $SCENARIO "NONE"
Record "Safari" $SCENARIO $SCENARIO "NONE"
Record "Edge" $SCENARIO $SCENARIO "NONE"

SCENARIO="idle_on_youtube"
Record "Chrome" $SCENARIO $SCENARIO "NONE"
Record "Safari" $SCENARIO $SCENARIO "NONE"
Record "Edge" $SCENARIO $SCENARIO "NONE"

#TODO: Find a way to start the recording once everything is loaded. Or we continue ignoring all the first readings?
#TODO: Add the generation as part of running discharge
