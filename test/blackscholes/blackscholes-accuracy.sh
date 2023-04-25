#!/bin/bash

NUM_BUCKETS=$1

outputs/reg_blackscholes 1 test/blackscholes/in_10M.txt reg.out
outputs/nocap_blackscholes_$NUM_BUCKETS 1 test/blackscholes/in_10M.txt nocap.out
python3 ./test/blackscholes/blackscholes-accuracy.py reg.out nocap.out