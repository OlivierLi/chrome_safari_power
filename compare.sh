#! /bin/zsh

set -eu

# Get the functions
source ./check_env.sh

POWERLOG=/Applications/Intel\ Power\ Gadget/Powerlog

# Whether the test should start the browser and wait for the process to
# complete before running the scenario or whether the driver script should
# start the browser and it should then be accounted in the power use.
WAIT_FOR_STARTUP=true

function RecordPower()
{
  mkdir -p $OUTPUT_DIR/$2

  if [ "$1" = "Safari" ]; then
      # Safari needs this housekeeping to clear all open tabs otherwise
      # they get restored.
      open -a Safari
      osascript ./driver_scripts/prep_safari.scpt;
  fi

  if [ "$WAIT_FOR_STARTUP" = "true" ]; then
    if [ "$1" = "Safari" ]; then
      # Safari needs this housekeeping to clear all open tabs otherwise
      # they get restored.
      open -a Safari
      osascript ./driver_scripts/prep_safari.scpt;
      open -a Safari
    elif [ "$1" = "Chromium" ]; then
      open $CHROMIUM_APP --args  --user-data-dir="/tmp/UserDataDir/" --profile-directory="$4" $5
    elif [ "$1" = "Chrome" ]; then
      open -a 'Google Chrome' --args  --user-data-dir="/tmp/UserDataDir/" --profile-directory="$4" $5
    else
      echo "Invalid app chosen!";
      exit 127
    fi

    # Leave some time for the browser to start to avoid capturing startup.
    sleep 10
  fi

  # TODO: Put this behind an arg so we don't start power gadget.
  # Record the power usage.
  #$POWERLOG -resolution 100 -file $OUTPUT_DIR/$2/navigation.$i.csv -cmd osascript $3;

  osascript $3;
}

function RecordChrome(){
  # This script uses the open command which needs the path to the .app
  CHROMIUM_APP=/tmp/signed_baseline/Chromium-87.0.4273.0/Chromium.app

  # TODO: Check signing with this: codesign --verify --verbose

  #osascript ./driver_scripts/chrome_setup_idle_on_site.scpt
  RecordPower "Chromium" "Chromium" ./driver_scripts/chrome_navigation.scpt "Baseline" "";

  # If kill fail abort. It means the browser quit itself.
  killall "Chromium"
}

function RecordChromeExperiment(){
  # This script uses the open command which needs the path to the .app
  CHROMIUM_APP=/tmp/signed/Chromium-87.0.4273.0/Chromium.app

  #osascript ./driver_scripts/chrome_setup_idle_on_site.scpt
  RecordPower "Chromium" "ChromiumExperiment" ./driver_scripts/chrome_navigation.scpt "Experiment" "--disable-site-isolation-trials";

  # If kill fail abort. It means the browser quit itself.
  killall "Chromium"
}

function RecordSystemIdle(){
  RecordPower "Idle" "Idle" ./driver_scripts/idle.scpt;
}

function RecordSafari(){
  #osascript ./driver_scripts/safari_setup_idle_on_site.scpt
  RecordPower "Safari" "Safari" ./driver_scripts/safari_navigation.scpt;

  # If kill fail abort. It means the browser quit itself.
  killall "Safari"
}

function ChromeVsSafari(){
  RecordChrome
  RecordSafari
}

function ChromeVsChrome(){
  RecordChrome

  # For some reason macOS does not like consecutive calls to
  # open/kill for the same app. Add a useless open and close of finder
  # right here in case Chromium is tested twice.
  osascript ./driver_scripts/finder.scpt

  RecordChromeExperiment
}

function Run(){
  OUTPUT_DIR=/Users/olivier/Documents/SiteIsolationIdle/
  CheckEnv

  # Kill all browsers just to be sure.
  killall -9 "Chromium" || true
  killall -9 "Safari" || true

  for i in $(seq 1 60); do 
    echo "Run #$i";

    ChromeVsChrome

  done
}

# Use this function to try and record the fraction of system
# power that is consumed by the Intel package.
function IsolateCPUPower(){
  # Use AMD gpu to ignore it in PowerMonitor.
  GPU_MODE="20"
  WAIT_FOR_STARTUP=false
  CheckEnv

  # We don't need to keep the results around.
  OUTPUT_DIR=/tmp/power_readings/

  # Kill all browsers just to be sure.
  killall -9 "Chromium" || true
  killall -9 "Safari" || true

  # Not in a loop, set $i.
  i=1

  GetPowerProperty "Charge Remaining" CAPACITY_BEFORE 
  RecordChrome
  local energy_used=$(cat $OUTPUT_DIR/Chromium/navigation.1.csv | grep "Cumulative Package Energy_0 (mWh)" | cut -d "=" -f 2 | awk '{$1=$1};1' | sed 's/.$//')
  GetPowerProperty "Charge Remaining" CAPACITY_AFTER 
  echo "Chromium, $CAPACITY_BEFORE, $CAPACITY_AFTER, $energy_used" >> results/chrome.csv;

  GetPowerProperty "Charge Remaining" CAPACITY_BEFORE 
  RecordSafari
  local energy_used=$(cat $OUTPUT_DIR/Safari/navigation.1.csv | grep "Cumulative Package Energy_0 (mWh)" | cut -d "=" -f 2 | awk '{$1=$1};1' | sed 's/.$//')
  GetPowerProperty "Charge Remaining" CAPACITY_AFTER 
  echo "Safari, $CAPACITY_BEFORE, $CAPACITY_AFTER, $energy_used" >> results/safari.csv;

  GetPowerProperty "Charge Remaining" CAPACITY_BEFORE 
  RecordSystemIdle
  local energy_used=$(cat $OUTPUT_DIR/Idle/navigation.1.csv | grep "Cumulative Package Energy_0 (mWh)" | cut -d "=" -f 2 | awk '{$1=$1};1' | sed 's/.$//')
  GetPowerProperty "Charge Remaining" CAPACITY_AFTER 
  echo "Idle, $CAPACITY_BEFORE, $CAPACITY_AFTER, $energy_used" >> results/idle.csv;
}

#Run
