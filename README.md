# NOCAP
**N**earby-**o**perand **C**ontinuous **Ap**proximation (NOCAP) is a project created by Neel Shah, Owen Goebel, Peter Ly, Zhixiang Teoh for EECS 583 Advanced Compilers at the University of Michigan.

## Overview

We implement an algorithm that approximates continuous functions with a lookup table with the goal of sacrificing significant memory usage and some accuracy for speed. Specifically, we:
1. Gather profile data (we can omit this step for periodic functions)
2. Use the profile data to build intervals of input to approximate the function
3. Use the profile data to estimate the granularity of the intervals and build input buckets
4. Build a lookup table.
5. Replace all calls to function of interest with a call to the lookup table.

## Usage

Example usage, given a test program `<project-root>/test/test_exp_log.c`:


```sh
# Directory structure
# .
# ├── CMakeLists.txt
# ├── Makefile
# ├── README.md
# ├── experimental/
# ├── nocap.py
# ├── passes
# │   ├── CMakeLists.txt
# │   └── collect_profile.cpp
# ├── setup.sh
# └── test
#     └── exp_log
#         ├── test_exp_log.c
#     └── blackscholes
#         ├── blackscholes.c

# Create `build`, `outputs` directories, execute LLVM pass on test/*.c
make setup
# Run NOCAP on test/blackscholes/blackscholes.c, approximating `log` functions
python3 nocap.py -t blackscholes -f log -args "1 test/blackscholes/in_10M.txt /dev/null" build

# Compile the original and NOCAP'd programs
gcc -o outputs/reg_blackscholes test/blackscholes/blackscholes.c -lm
gcc -o outputs/nocap_blackscholes build/src/blackscholes_lookups.c build/src/nocap_log.c -lm

# Compare the runtime of the original and NOCAP'd programs
time outputs/reg_blackscholes
time outputs/nocap_blackscholes
```