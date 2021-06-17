#! /bin/bash

set -eu 

cd "$(dirname "$0")"

rm -rf samples
mkdir -p samples

python3 stack_collapse.py --stack_dir $1 > samples/samples.collapsed
python3 filter.py --mode cpu_time --stack_file samples/samples.collapsed > samples/samples.collapsed.filtered
python3 filter.py --mode clean_only --stack_file samples/samples.collapsed > samples/samples.collapsed.cleaned
