# NOCAP
**N**earby-**o**perand **C**ontinuous **Ap**proximation (NOCAP) is a project created by Neel Shah, Owen Goebel, Peter Ly, Zhixiang Teoh for EECS 583 Advanced Compilers at the University of Michigan.

## Overview

We implement an algorithm that approximates continuous functions with a lookup table with the goal of sacrificing significant memory usage and some accuracy for speed. Specifically, we:
1. Gather profile data (we can omit this step for periodic functions)
2. Use the profile data to build intervals of input to approximate the function
3. Use the profile data to estimate the granularity of the intervals and build input buckets
4. Build a lookup table.
5. Replace all calls to function of interest with a call to the lookup table.

```
$ python3 nocap.py
usage: nocap.py [-h] [-func FUNC] [-funcs FUNCS [FUNCS ...]]
                [-testName TESTNAME] [-args ARGS] [-bucketsFill]
                [-numBuckets NUMBUCKETS]
                {build,build_from_file,clean,build_profile} ...

Run NOCAP.

options:
  -h, --help            show this help message and exit
  -func FUNC            Name of the function to create lookup table for.
  -funcs FUNCS [FUNCS ...]
                        Names of the functions to create lookup tables
                        for.
  -testName TESTNAME    Name of the folder within test/ in which the test
                        file is located.
  -args ARGS            Command line arguments for test file (optional)
  -bucketsFill          Fill buckets with function computed for median of
                        bucket.
  -numBuckets NUMBUCKETS
                        Number of buckets to use to build lookup table.

Commands:
  {build,build_from_file,clean,build_profile}
    build               Build profile and generate new source files
    build_from_file     Use file to generate new source files
    clean               Remove created files
    build_profile       Apply llvm pass to sources and build profile file
```

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
#         ├── exp_log.c
#     └── blackscholes
#         ├── blackscholes.c

# Create `build`, `outputs` directories, execute LLVM pass on test/*.c
make setup
# Run NOCAP on test/blackscholes/blackscholes.c, approximating `log` functions
python3 nocap.py -t blackscholes -f log -args "1 test/blackscholes/in_10M.txt /dev/null" -b build

# Compile the original and NOCAP'd programs
gcc -o outputs/reg_blackscholes test/blackscholes/blackscholes.c -lm
gcc -o outputs/nocap_blackscholes build/src/blackscholes_lookups.c build/src/nocap_log.c -lm

# Compare the runtime of the original and NOCAP'd programs
time outputs/reg_blackscholes 1 test/blackscholes/in_10M.txt /dev/null # Read real time
time outputs/nocap_blackscholes 1 test/blackscholes/in_10M.txt /dev/null # Read real time

# Measure normalized error between original and NOCAP'd programs
test/blackscholes/blackscholes-accuracy.sh
```