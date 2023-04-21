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
#     └── test_exp_log.c

# Create `build`, `outputs` directories, execute LLVM pass on test/*.c
make setup
# Run NOCAP on test_exp_log.c, approximating `log` functions
python3 nocap.py -t test_exp_log -f log
# Compare the output of the original and NOCAP'd programs
make compare_exp_log FUNC=log
```