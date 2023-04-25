#!/bin/bash
NUM_BUCKETS=(1000 3000 5000 10000)

# # 10 to 500 in steps of 10
# for (( i=1; i<10; i+=1 )); do
#   NUM_BUCKETS+=($i)
# done

# for (( i=10; i<=100; i+=10 )); do
#   NUM_BUCKETS+=($i)
# done

FUNC=$1
OUTPUT_FILE="blackscholes-accuracy-vs-buckets-$FUNC.txt"
# Clear the output file blackscholes-accuracy-vs-buckets.txt
# echo -n "" > $OUTPUT_FILE

# Build profile for {FUNC} if it doesn't exist
if [ ! -f "build/out/$FUNC_out" ]; then
    python3 nocap.py -t blackscholes -func $FUNC -args "1 test/blackscholes/in_10M.txt /dev/null" build_profile
fi

gcc -o outputs/reg_blackscholes test/blackscholes/blackscholes.c -lm

for num_buckets in "${NUM_BUCKETS[@]}"; do
    echo "Running with $num_buckets buckets, approximating $FUNC function"
    python3 nocap.py -t blackscholes -func $FUNC -b -n $num_buckets build_from_file
    gcc -o outputs/nocap_blackscholes_$num_buckets build/src/blackscholes_lookups.c build/src/nocap_$FUNC.c -lm
    test/blackscholes/blackscholes-accuracy.sh $num_buckets >> $OUTPUT_FILE
done
