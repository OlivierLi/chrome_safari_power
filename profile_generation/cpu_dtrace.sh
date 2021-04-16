#! /bin/bash

set -eux 

cd "$(dirname "$0")"

if cd Flamegraph; then git pull && cd ..; else git clone https://github.com/brendangregg/FlameGraph; fi
rm -rf samples
mkdir -p samples
cat $1/* | ./Flamegraph/stackcollapse.pl > samples/samples.collapsed
python3 filter.py --mode cpu_time --stack_file samples/samples.collapsed > samples/samples.collapsed.filtered
cat ./samples/samples.collapsed.filtered | ./Flamegraph/flamegraph.pl -w 3000 > ./samples/cpu_flames.svg
