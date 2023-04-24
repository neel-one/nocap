#!/bin/bash

./outputs/reg_blackscholes 1 test/blackscholes/in_10M.txt reg.out
./outputs/nocap_blackscholes 1 test/blackscholes/in_10M.txt nocap.out
python3 blackscholes-accuracy.py reg.out nocap.out