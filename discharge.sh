#! /bin/zsh

set -eu

# Get the functions
source check_env.sh

CheckEnv

# Whether the test should start the browser and wait for the process to
# complete before running the scenario or whether the driver script should
# start the browser and it should then be accounted in the power use.
WAIT_FOR_STARTUP=true

function RecordPower()
{
  mkdir -p $OUTPUT_DIR/$2

  if [ "$WAIT_FOR_STARTUP" = "true" ]; then
    if [ "$1" = "Safari" ]; then
      # Safari needs this housekeeping to clear all open tabs otherwise
      # they get restored.
      open -a Safari
      osascript ./driver_scripts/prep_safari.scpt;
      open -a Safari
    elif [ "$1" = "Chromium" ]; then
      open $CHROMIUM_APP --args  --user-data-dir="/tmp/UserDataDir_$1/" --profile-directory="$4" $5
    elif [ "$1" = "Chrome" ]; then
      open -a 'Google Chrome' --args  --user-data-dir="/tmp/UserDataDir_$1/" --profile-directory="$4" $5
    elif [ "$1" = "Edge" ]; then
      open -a 'Microsoft Edge' --args  --user-data-dir="/tmp/UserDataDir_$1/" --profile-directory="$4" $5
    else
      echo "Invalid app chosen!";
      exit 127
    fi
  fi

  if [ "$6" != "NONE" ]
  then
    osascript $6;
  fi

  # Start the collection of Power.Mac.BatteryDischarge
  ./bin/Power.Mac.BatteryDischarge&
  osascript $3;
}

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

  # Run the scenario.
  OUTPUT_DIR=./results
  RecordPower $1 $1 ./driver_scripts/${1}_${2}.scpt "Experiment" "" $4

  KillALL

  # Rename the results and save.
  mv battery_discharge.csv ./results/$1/$3.csv
}

./generate_scripts.py

SCENARIO="zero_window"
Record "Chrome" $SCENARIO $SCENARIO "NONE"
Record "Safari" $SCENARIO $SCENARIO "NONE"

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
