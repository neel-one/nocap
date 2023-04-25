#!/bin/bash

FUNCS=("log" "sqrt" "exp")

NUM_BUCKETS=(500 600 700 800)

# Benchmark accuracy vs #buckets for all functions approximated
OUTPUT_FILE="blackscholes-accuracy-vs-buckets-combined.txt"
# Clear the output file blackscholes-accuracy-vs-buckets.txt
echo -n "" > $OUTPUT_FILE

# Build profile for {func} if it doesn't exist
for func in "${FUNCS[@]}"; do
    if [ ! -f "build/out/$func_out" ]; then
        python3 nocap.py -t blackscholes -func $func -args "1 test/blackscholes/in_16.txt /dev/null" build_profile
    fi
done

gcc -o outputs/reg_blackscholes test/blackscholes/blackscholes.c -lm

for num_buckets in "${NUM_BUCKETS[@]}"; do
    echo "Running with $num_buckets buckets, approximating ${FUNCS[@]} functions"
    # Check that all nocap_{func}.c files exist
    python3 nocap.py -t blackscholes -funcs "${FUNCS[@]}" -b -n $num_buckets build_from_file

    C_FUNC_SRCS=()
    for func in "${FUNCS[@]}"; do
        C_FUNC_SRCS+=("build/src/nocap_$func.c ")
    done
    # Remove trailing space
    C_FUNC_SRCS=${C_FUNC_SRCS[@]%" "}
    gcc -o outputs/nocap_blackscholes_$num_buckets build/src/blackscholes_lookups.c $C_FUNC_SRCS -lm

    test/blackscholes/blackscholes-accuracy.sh $num_buckets >> $OUTPUT_FILE
done
