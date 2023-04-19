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

def build_from_file():
    # Do something for the generate command
    p = Path('build/src')
    p.mkdir(exist_ok=True)

    for path in Path('test').glob('*.c'):
        shutil.copy(path, p/path.name)

    header = p/f'nocap_{args.func}.h'
    source = p/f'nocap_{args.func}.c'

    header.touch(exist_ok=True)
    source.touch(exist_ok=True)

    header_code = f'''// TODO: properly implement
#include <stdio.h>
#define begin 0
#define end 100
#define granularity 5
#define last_index (end - begin)/granularity
double nocap_{args.func}(double x);
    '''
    header.write_text(header_code)

    source_code = f'''// TODO: properly implement
#include "nocap_{args.func}.h"
double tb[] = {{

}};
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
clean_parser = subparsers.add_parser('clean', help='Remove created files')

# Parse the command line arguments
args = parser.parse_args()

# Call the appropriate function based on the command line arguments
if args.command == 'build':
    build()
elif args.command == 'build_from_file':
    build_from_file()
elif args.command == 'clean':
    clean()
else:
    parser.print_help()
