import argparse
from pathlib import Path
import shutil
import subprocess


def build():
    build_profile()
    build_from_file('build/tmp/a_out')


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
    # TODO: take in potential command line input
    out = subprocess.run(
        f'build/tmp/a {args.args} > build/tmp/a_out', shell=True)
    print(out)


def clean():
    p = Path('build/src')
    for path in p.glob('*'):
        path.unlink()
    p = Path('build/tmp')
    for path in p.glob('*'):
        path.unlink()


def analyze_file(file):
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
    num_buckets = 100
    granularity = (end - begin)/num_buckets
    print(f'Start = {begin}, End = {end}, Granularity = {granularity}')
    tb = [None for _ in range(int((end-begin)/granularity) + 1)]
    for i in range(len(X)):
        # TODO: handle -inf, inf, nan
        bucket = int((X[i]-begin)/granularity)
        tb[bucket] = str(Y[i])
    for i in range(len(tb)):
        if tb[i] is None:
            tb[i] = tb[i-1]
    table_string = f'''double nocap_{args.func}_tb[] = {{ {','.join(tb)} }};'''
    return {
        'begin': begin,
        'end': end,
        'table_string': table_string,
        'granularity': granularity
    }


def build_from_file(file):
    if args.func is None:
        print("ERROR: You must specify a -func argument to finish your build!!!")
        exit(1)
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
    # for path in Path('test').glob('*.c'):
    #    shutil.copy(path, p/path.name)
        # Append '_lookups' to original source file name to reflect slight modifications
    #    shutil.move(p/path.name, p/f'{path.stem}_lookups.c')

    header = p/f'nocap_{args.func}.h'
    source = p/f'nocap_{args.func}.c'

    header.touch(exist_ok=True)
    source.touch(exist_ok=True)

    analysis = analyze_file(file)

    header_code = f'''
#include <stdio.h>
#define nocap_{args.func}_begin {analysis['begin']}
#define nocap_{args.func}_end {analysis['end']}
#define nocap_{args.func}_granularity {analysis['granularity']}
#define nocap_{args.func}_last_index (nocap_{args.func}_end - nocap_{args.func}_begin) / nocap_{args.func}_granularity

extern double nocap_{args.func}(double x);
'''
    header.write_text(header_code)

    source_code = f'''#include <math.h>
#include "nocap_{args.func}.h"

{analysis['table_string']}
double nocap_{args.func}(double x) {{
    int index = (x - nocap_{args.func}_begin)/nocap_{args.func}_granularity;
    if (index > nocap_{args.func}_last_index || index < 0) {{
        // Fall back to {args.func}
    }}
    return nocap_tb[index];
}}
'''
    source.write_text(source_code)

    funcs = []
    for file in p.glob("nocap_*.h"):
        funcs.append(file.name[len('nocap_'):-2])
    text = ''
    for func in funcs:
        text += f'''#include "nocap_{func}.h"
#define {func}(x) nocap_{func}(x)
'''
    for path in p.glob('*.c'):
        if 'nocap' not in str(path):
            path.write_text(text + path.read_text())


# Set up the argument parser
parser = argparse.ArgumentParser(description='Run NOCAP.')
parser.add_argument('-func', type=str,
                    help='Name of the function to create lookup table for.')
parser.add_argument('-testName', type=str,
                    help='Name of the folder within test/ in which the test file is located.')
parser.add_argument('-args', type=str, default='',
                    help='Command line arguments for test file (optional)')

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
