#! /bin/zsh
set -eu

# Get the functions
source ./functions.sh

CheckEnv

GetPowerProperty "Charge Remaining" CAPACITY_BEFORE 
echo "Capacity before run: $CAPACITY_BEFORE"

GetPowerProperty "Charge Remaining" CAPACITY_AFTER 
echo "Capacity after run: $CAPACITY_AFTER"
