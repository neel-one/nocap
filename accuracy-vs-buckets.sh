#!/bin/bash
NUM_BUCKETS=()

# 10 to 500 in steps of 10
for (( i=10; i<=500; i+=10 )); do
  NUM_BUCKETS+=($i)
done

OUTPUT_FILE="blackscholes-accuracy-vs-buckets.txt"
# Clear the output file blackscholes-accuracy-vs-buckets.txt
echo -n "" > $OUTPUT_FILE

for num_buckets in "${NUM_BUCKETS[@]}"; do
    python3 nocap.py clean
    echo "Running with $num_buckets buckets"
    python3 nocap.py -t blackscholes -f log -b -args "1 test/blackscholes/in_10M.txt /dev/null" -n $num_buckets build
    gcc -o outputs/reg_blackscholes_$num_buckets test/blackscholes/blackscholes.c -lm
    gcc -o outputs/nocap_blackscholes_$num_buckets build/src/blackscholes_lookups.c build/src/nocap_log.c -lm
    test/blackscholes/blackscholes-accuracy.sh $num_buckets >> $OUTPUT_FILE
done
