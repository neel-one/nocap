import argparse
from pathlib import Path
import shutil
import subprocess
import re


def build():
    build_profile()
    build_from_file(f'build/out/{args.func}_out')


def build_profile():
    srcs = []
    if args.testName is None:
        print("ERROR: You must specify a -testName argument to build!!!")
        exit(1)
    test_dir = Path('test')/args.testName
    for path in test_dir.glob(f'*.c'):
        srcs.append(f'{path}')
        # TODO: support multiple source files
        assert len(srcs) == 1  # Otherwise `clang -emit-llvm` will fail
    src_string = ' '.join(srcs)
    wd = Path('build')
    Path(wd/'tmp').mkdir(exist_ok=True)
    out = subprocess.run(
        f'clang -emit-llvm {src_string} -c -o build/tmp/test.bc', shell=True)
    print(out)
    out = subprocess.run(
        f'opt -enable-new-pm=0 -load build/passes/LLVMPJT.so -fppass -fppass-func-name={args.func} -o build/tmp/a.bc < build/tmp/test.bc > /dev/null', shell=True)
    print(out)
    out = subprocess.run('llc tmp/a.bc -o tmp/a.s', cwd=wd, shell=True)
    print(out)
    # TODO: make this resilient to user LDFlags/Compiler flags (they should define compilation not us...)
    out = subprocess.run(
        'clang tmp/a.s -no-pie -lm -o tmp/a', cwd=wd, shell=True)
    print(out)
    out = subprocess.run(
        f'build/tmp/a {args.args} > build/out/{args.func}_out', shell=True)
    print(out)


def clean():
    p = Path('build/src')
    for path in p.glob('*'):
        path.unlink()
    p = Path('build/tmp')
    for path in p.glob('*'):
        path.unlink()


def analyze_file(file, func):
    with open(file) as f:
        nums = f.read().split()
    nums = [s[2:] for s in nums if s.startswith('@@')]
    assert len(nums) % 2 == 0
    # X := profiled inputs to function
    X = [float(nums[i]) for i in range(0, len(nums), 2)]
    # Y := profiled outputs of function
    Y = [float(nums[i+1]) for i in range(0, len(nums), 2)]
    begin = min(X)
    end = max(X)
    # granularity = float('inf')
    # for i in range(len(X)):
    #     for j in range(i+1, len(X)):
    #         granularity = min(granularity, abs(X[j]-X[i]))

    # For simplicity, assume 100 buckets
    # TODO: define granularity in a more sophisticated manner
    num_buckets = args.numBuckets
    granularity = (end - begin)/num_buckets
    print(f'Start = {begin}, End = {end}, Granularity = {granularity}')
    tb = [None for _ in range(num_buckets)]

    #### Use median of bucket to compute function value for bucket ####
    if args.bucketsFill:
        proxy_computer_source = f'''#include <math.h>
#include <stdio.h>

int main(int argc, char** argv) {{
    double tb[{num_buckets}] = {{}};

'''
        for bucket in range(num_buckets):
            median_of_bucket = begin + \
                (bucket*granularity + (bucket+1)*granularity)/2
            proxy_computer_source += f'''    tb[{bucket}] = {func}({median_of_bucket});
'''

        proxy_computer_source += f'''
    for (int i = 0; i < {num_buckets}; ++i) {{
        printf("%f ", tb[i]);
    }}
}}
'''

        # Create tmp/proxy_computer.c
        with open('build/tmp/proxy_computer.c', 'w') as f:
            f.write(proxy_computer_source)
        # Compile tmp/proxy_computer.c
        out = subprocess.run(
            'clang build/tmp/proxy_computer.c -lm -o build/tmp/proxy_computer', shell=True)
        print(out)
        # Run tmp/proxy_computer
        out = subprocess.run(
            './build/tmp/proxy_computer > build/tmp/proxy_computer_out', shell=True)
        print(out)
        # Read tmp/proxy_computer_out
        with open('build/tmp/proxy_computer_out') as f:
            tb = f.read().split()

    else:  # Use only test program's outputs ####
        for i in range(len(X)):
            # TODO: handle -inf, inf, nan
            bucket = int((X[i]-begin)/granularity) - 1  # 0-indexed
            tb[bucket] = str(Y[i])

        for bucket in range(num_buckets):
            if tb[bucket] is None:
                tb[bucket] = tb[bucket-1]

    table_string = f'''double nocap_{func}_tb[] = {{ {', '.join(tb)} }};'''
    return {
        f'{func}': {
            'begin': begin,
            'end': end,
            'table_string': table_string,
            'granularity': granularity
        }
    }


def build_from_file(file):
    if args.func is None and args.funcs is None:
        print("ERROR: You must specify either a -func or -funcs argument to finish your build!!!")
        exit(1)

    # Either build with multiple functions approximated, or just one. NOT both.
    assert (args.func is not None) ^ (args.funcs is not None)

    # Just use the executable corresponding to any one of the functions
    func = args.func if args.func is not None else args.funcs[0]
    file = f'build/out/{func}_out'

    # Do something for the generate command
    p = Path('build/src')
    p.mkdir(exist_ok=True)
    if args.testName is None:
        print("ERROR: You must specify a -testName argument to build!!!")
        exit(1)
    test_dir = Path('test')/args.testName
    for path in test_dir.glob(f'*.c'):
        shutil.copy(path, p/path.name)
        shutil.move(p/path.name, p/f'{path.stem}_lookups.c')

    # Create .h, .c for each function-to-approximate
    lookups_text = ''
    funcs = args.funcs if args.funcs is not None else [args.func]
    for func in funcs:
        header = p/f'nocap_{func}.h'
        source = p/f'nocap_{func}.c'

        header.touch(exist_ok=True)
        source.touch(exist_ok=True)

        analysis = analyze_file(file, func)

        header_code = f'''
#include <stdio.h>
#define nocap_{func}_begin {analysis[func]['begin']}
#define nocap_{func}_end {analysis[func]['end']}
#define nocap_{func}_granularity {analysis[func]['granularity']}
#define nocap_{func}_last_index (nocap_{func}_end - nocap_{func}_begin) / nocap_{func}_granularity

extern double nocap_{func}(double x);
'''
        header.write_text(header_code)

        source_code = f'''#include <math.h>
#include "nocap_{func}.h"

{analysis[func]['table_string']}

double nocap_{func}(double x) {{
    int bucket_idx = (x - nocap_{func}_begin)/nocap_{func}_granularity;
    if (bucket_idx > nocap_{func}_last_index || bucket_idx < 0) {{
        // Fall back to {func}
        return {func}(x);
    }}
    return nocap_{func}_tb[bucket_idx];
}}
'''
        source.write_text(source_code)

    # Add #include "nocap_{func}.h" to all .c files in build/src
        lookups_text += f'''#include "nocap_{func}.h"
'''

    # Replace calls to func with nocap_{func} calls
    for path in p.glob('*.c'):
        if 'nocap' not in str(path):
            path.write_text(lookups_text + path.read_text())
            for func in funcs:
                path.write_text(re.sub(
                    rf'\b{func}\b', f'nocap_{func}', path.read_text()))


# Set up the argument parser
parser = argparse.ArgumentParser(description='Run NOCAP.')
parser.add_argument('-func', type=str,
                    help='Name of the function to create lookup table for.')
parser.add_argument('-funcs', type=str, nargs='+',
                    help='Names of the functions to create lookup tables for.')
parser.add_argument('-testName', type=str,
                    help='Name of the folder within test/ in which the test file is located.')
parser.add_argument('-args', type=str, default='',
                    help='Command line arguments for test file (optional)')
parser.add_argument('-bucketsFill', default=False, action='store_true',
                    help='Fill buckets with function computed for median of bucket.')
parser.add_argument('-numBuckets', type=int, default=100,
                    help='Number of buckets to use to build lookup table.')

# Create subparsers for the build and generate commands
subparsers = parser.add_subparsers(title='Commands', dest='command')
build_parser = subparsers.add_parser(
    'build', help='Build profile and generate new source files')
file_parser = subparsers.add_parser(
    'build_from_file', help='Use file to generate new source files')
file_parser.add_argument('-file', type=str,
                         help='File to build lookup table from formatted as space delimited x, y pairs (e.g. x1 y1 x2 y2)')
clean_parser = subparsers.add_parser('clean', help='Remove created files')
profile_parser = subparsers.add_parser(
    'build_profile', help='Apply llvm pass to sources and build profile file')

# Parse the command line arguments
args = parser.parse_args()

# Call the appropriate function based on the command line arguments
if args.command == 'build':
    build()
elif args.command == 'build_profile':
    build_profile()
elif args.command == 'build_from_file':
    build_from_file(args.file)
elif args.command == 'clean':
    clean()
else:
    parser.print_help()
