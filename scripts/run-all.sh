#!/usr/bin/env bash

set -xeuo pipefail

script_dir=$(dirname "$(readlink -f "$0")")
cd "$script_dir"

./estimate-intel-performance.py
./scheduler.py # scheduler produces a csv file read by speedup, keep this order
./speedup.py
./sched_preprocess.py # keep the order of sched_* too
./sched_scoring.py
./sched_plot.py
./time-multi-fpga.py
./time-xilinx.py
./time-breakdown.py
./time-intel.py
./time-rosetta-xilinx.py
./throughput-motivation.py
./throughput.py
./overheads.py
./time-memory.py
./memory-channels-total.py
./memory-channels-fpga.py
./oversub.py
./fstate-oh.py
./migration-checkpoint.py
