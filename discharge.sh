#! /bin/zsh

set -eux

source check_env.sh

CheckEnv

# Kill all browsers just to be sure.
killall -9 "Chromium" || true
killall -9 "Safari" || true

# Make sure we're not already recording
killall Power.Mac.BatteryDischarge || true

# Local paths
BIN=/Users/olivier/Library/Developer/Xcode/DerivedData/Power.Mac.BatteryDischarge-frtspoojsdrdsycbpuzpwyqlczdp/Build/Products/Debug/Power.Mac.BatteryDischarge

# Get the functions
source ./check_env.sh
source ./compare.sh

BROWSER="Safari"
SCENARIO="idle_on_site"

# Start the collection of Power.Mac.BatteryDischarge
$BIN&

# Run the scenario.
OUTPUT_DIR=./results

RecordPower "Safari" "Safari" ./driver_scripts/safari_setup_idle_on_site.scpt;

# Stop recording
killall Power.Mac.BatteryDischarge

# Rename the results and save.
mv battery_discharge.csv ./results/$BROWSER/$SCENARIO.csv
