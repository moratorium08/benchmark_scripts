import os
import sys
import argparse
import difflib

script_dir = os.path.dirname(os.path.abspath(__file__))
bench_dir = os.path.join(script_dir, "../benchmark/inputs/25-adt-chc-comp/")

parser = argparse.ArgumentParser()
parser.add_argument('--benchmark', nargs='?', default=bench_dir,
                    help='Benchmark directory')
parser.add_argument('filename', metavar='filename',
                    help='filename')

args = parser.parse_args()

with open(args.filename, "r") as f:
    target = f.readlines()

#inputs = os.path.join(bench_dir, "inputs")
inputs = bench_dir

min_diff = None
closest_files = []

def diff_line_count(a, b):
    """Compute the number of differing lines using difflib"""
    diff = list(difflib.unified_diff(a, b))
    return sum(1 for line in diff if line.startswith('+ ') or line.startswith('- '))

for root, _, files in os.walk(inputs):
    for fname in files:
        path = os.path.join(root, fname)
        try:
            with open(path, "r") as f:
                content = f.readlines()

            diff_count = diff_line_count(target, content)

            if min_diff is None or diff_count < min_diff:
                min_diff = diff_count
                closest_files = [os.path.relpath(path, inputs)]
            elif diff_count == min_diff:
                closest_files.append(os.path.relpath(path, inputs))

        except Exception as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)

if not closest_files:
    print("unknown file")
    sys.exit(-1)

print("Most similar file(s):")
for fname in closest_files:
    print(fname)

