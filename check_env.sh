#! /bin/zsh
set -eu

# By default intel GPU should be used on battery.
GPU_MODE="20"

function SystemProfilerProperty()
{
  local result=$2
  local local_result=$(system_profiler $3| grep -i $1 | cut -d ":" -f 2 | awk '{$1=$1};1')
  eval $result="'$local_result'"
}

function GetPowerProperty()
{
  SystemProfilerProperty $1 $2 "SPPowerDataType"
}

function GetDisplayProperty()
{
  SystemProfilerProperty $1 $2 "SPDisplaysDataType"
}

function CompareValue()
{
  if [ "$1" != "$2" ]; then
    echo $3
    exit 127
  fi
}

CheckPowerValue()
{
  # Query value, remove newlines.
  GetPowerProperty $1 VALUE
  VALUE=$(echo $VALUE|tr -d '\n')

  CompareValue $VALUE $2 $3
}

CheckDisplayValue()
{
  # Query value, remove newlines.
  GetDisplayProperty $1 VALUE
  VALUE=$(echo $VALUE|tr -d '\n')

  CompareValue $VALUE $2 $3
}

function CheckProgramNotRunning(){
  if pgrep -x "$1" > /dev/null; then
    echo "$2"
    exit 127
  fi
}

function CheckEnv()
{
  # Use command: pmset -c gpuswitch 2 to allow dynamic gpu switching on charger.
  # Use command: pmset -b gpuswitch 0 to force Intel on battery.
  #CheckPowerValue "gpuswitch" "$GPU_MODE" "GPU mode invalid."

  # Validate power setup.
  CheckPowerValue "charging" "NoNo" "Laptop cannot be charging during test."
  CheckPowerValue "connected" "No" "Charger cannot be connected during test."

  # Validate display setup.
  CheckDisplayValue "Automatically adjust brightness" "No" "Disable automatic brightness adjustments and unplug external monitors"

  # Use Amphetamine.app to avoid sleeping during the tests.
  if ! pgrep -x "Amphetamine" > /dev/null; then
    echo "Use Amphetamine to prevent sleep."
    exit 127
  fi
  CompareValue $(defaults read com.if.Amphetamine "Default Duration") "0" "Default session length in Amphetamine should be unlimited";
  CompareValue $(defaults read com.if.Amphetamine "Start Session At Launch") "1" "Amphetamine session should be default launched to avoid forgetting.";

  # Verify that no terminals are running. They introduce too much overhead. (As measured with powermetrics)
  CheckProgramNotRunning "Terminal" "Do not have a terminal opened. Use SSH.";
  CheckProgramNotRunning "iTerm2" "Do not have a terminal opened. Use SSH.";

}

CheckEnv
