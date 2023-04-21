#!/bin/bash

# Initial setup to create directory structure and LLVM .so
# Create ./outputs/ directory if it doesn't exist
if [ ! -d "./outputs" ]; then
    mkdir outputs
fi
# Create ./build/ directory if it doesn't exist
if [ ! -d "./build" ]; then
    mkdir build
fi
cd build
cmake ..
make -j4
cd -
