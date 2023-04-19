import argparse
from pathlib import Path
import shutil

def build():
    # Do something for the build command
    print("Running build command...")

def clean():
    p = Path('build/src')
    for path in p.glob('*'):
        path.unlink()

def analyze_file(file):
    with open(file) as f:
        nums = f.read().split()
    assert len(nums)%2 == 0
    X = [float(nums[i]) for i in range(0, len(nums), 2)]
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
    tb = [None for _ in range(int((end-begin)/granularity) + 1)]
    for i in range(len(X)):
        bucket = int((X[i]-begin)/granularity)
        tb[bucket] = str(Y[i])
    for i in range(len(tb)):
        if tb[i] is None:
            tb[i] = tb[i-1]
    table_string = f'''double tb[] = {{ {','.join(tb)} }};'''
    return {
        'begin': begin,
        'end': end,
        'table_string': table_string,
        'granularity': granularity
    }

def build_from_file(file):
    # Do something for the generate command
    p = Path('build/src')
    p.mkdir(exist_ok=True)

    for path in Path('test').glob('*.c'):
        shutil.copy(path, p/path.name)

    header = p/f'nocap_{args.func}.h'
    source = p/f'nocap_{args.func}.c'

    header.touch(exist_ok=True)
    source.touch(exist_ok=True)

    analysis = analyze_file(file)

    header_code = f'''// TODO: properly implement
#include <stdio.h>
#define begin {analysis['begin']}
#define end {analysis['end']}
#define granularity {analysis['granularity']}
#define last_index (end - begin)/granularity
double nocap_{args.func}(double x);
    '''
    header.write_text(header_code)

    source_code = f'''// TODO: properly implement
#include "nocap_{args.func}.h"
// double tb[] = {{}};
{analysis['table_string']}
double nocap_{args.func}(double x) {{
    printf("Hello World");
    int index = (x - begin)/granularity;
    if (index > last_index || index < 0) {{
        // Fall back to {args.func}
    }}
    //return tb[index];
    return 0;
}}
    '''
    source.write_text(source_code)

    text = f'#include "nocap_{args.func}.h"\n#define {args.func}(x) nocap_{args.func}(x)\n'
    for path in p.glob('*.c'):
        if 'nocap' not in str(path):
            path.write_text(text + path.read_text())


# Set up the argument parser
parser = argparse.ArgumentParser(description='Run NOCAP.')
parser.add_argument('-func', type=str, help='Name of the function to create lookup table for.')

# Create subparsers for the build and generate commands
subparsers = parser.add_subparsers(title='Commands', dest='command')
build_parser = subparsers.add_parser('build', help='Build profile and generate new source files')
file_parser = subparsers.add_parser('build_from_file', help='Use file to generate new source files')
file_parser.add_argument('-file', type=str,
    help='File to build lookup table from formatted as space delimited x, y pairs (e.g. x1 y1 x2 y2)')
clean_parser = subparsers.add_parser('clean', help='Remove created files')

# Parse the command line arguments
args = parser.parse_args()

# Call the appropriate function based on the command line arguments
if args.command == 'build':
    build()
elif args.command == 'build_from_file':
    build_from_file(args.file)
elif args.command == 'clean':
    clean()
else:
    parser.print_help()
