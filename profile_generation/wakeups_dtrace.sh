#! /bin/bash

set -eu 

cd "$(dirname "$0")"

rm -rf samples
mkdir -p samples

python3 filter.py --mode wakeups --stack_dir $1 > samples/samples.collapsed.filtered
python3 filter.py --mode clean_only --stack_dir $1 > samples/samples.collapsed.cleaned
