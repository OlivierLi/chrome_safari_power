#! /bin/zsh
set -eu

function GetPowerProperty()
{
  local result=$2
  local local_result=$(system_profiler SPPowerDataType | grep -i $1 | cut -d ":" -f 2 | awk '{$1=$1};1')
  eval $result="'$local_result'"
}
