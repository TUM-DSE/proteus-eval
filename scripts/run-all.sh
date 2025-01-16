#!/usr/bin/env bash

set -xeuo pipefail

./scheduler.py # scheduler produces a csv file read by speedup, keep this order
./speedup.py
./time-compute.py
./time-memory.py
