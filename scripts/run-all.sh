#!/usr/bin/env bash

set -xeuo pipefail

script_dir=$(dirname "$(readlink -f "$0")")
cd "$script_dir"

./scheduler.py # scheduler produces a csv file read by speedup, keep this order
./speedup.py
./time-compute.py
./time-memory.py
