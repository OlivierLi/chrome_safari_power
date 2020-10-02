#! /bin/zsh

set -eu

# Get the functions
source ./check_env.sh

POWERLOG=/Applications/Intel\ Power\ Gadget/Powerlog
OUTPUT_DIR=/Users/olivier/Documents/Test/

function RecordPower()
{
  if [ "$1" = "Safari" ]; then
    # Safari needs this housekeeping to clear all open tabs otherwise
    # they get restored.
    open -a Safari
    osascript ./driver_scripts/prep_safari.scpt;
    open -a Safari
  elif [ "$1" = "Chromium" ]; then
    open $CHROMIUM_APP 
  else
    echo "Invalid app chosen!";
    exit 127
  fi

  # Leave some time for the browser to start to avoid capturing startup.
  sleep 10

  $POWERLOG -resolution 10 -file $OUTPUT_DIR/$2/navigation.$i.csv -cmd osascript $3;
  # If kill fail abort. It means the browser quit itself.
  killall $1
}

function RecordChrome(){
  # This script uses the open command which needs the path to the .app
  CHROMIUM_APP=/Users/olivier/git/chromium/src/out/Baseline/Chromium.app

  #osascript ./driver_scripts/chrome_setup_idle_on_site.scpt
  RecordPower "Chromium" "Chromium" ./driver_scripts/chrome_navigation.scpt;
}

function RecordSafari(){
  #osascript ./driver_scripts/safari_setup_idle_on_site.scpt
  RecordPower "Safari" "Safari" ./driver_scripts/safari_navigation.scpt;
}

function ChromeVsSafari(){
  RecordChrome
  RecordSafari
}

function ChromeVsChrome(){
  # For some reason macOS does not like consecutive calls to
  # open/kill for the same app. Add a useless open and close of finder
  # right here in case Chromium is tested twice.
  osascript ./driver_scripts/finder.scpt
}

function Run(){
  # Prep the directories.
  mkdir -p $OUTPUT_DIR/Chromium
  mkdir -p $OUTPUT_DIR/Safari

  # Kill all browsers just to be sure.
  killall -9 "Chromium" || true
  killall -9 "Safari" || true

  for i in $(seq 1 60); do 
    echo "Run #$i";
    ChromeVsSafari
  done
}

Run
