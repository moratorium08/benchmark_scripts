import os
import argparse
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
bench_dir = os.path.join(script_dir, "../benchmark")

parser = argparse.ArgumentParser()
parser.add_argument('--benchmark', nargs='?', default=bench_dir,
                    help='Benchmark directory')
parser.add_argument('filename', metavar='filename',
                    help='filename')

args = parser.parse_args()

with open(args.filename, "r") as f:
  target = f.read()


inputs = os.path.join(bench_dir, "inputs")

found = False
def find_file():
    for root, _, files in os.walk(inputs):
        for fname in files:
            path = os.path.join(root, fname)
            try:
                with open(path, "r") as f:
                    content = f.read()
                if content == target:
                    return os.path.relpath(path, inputs)
            except Exception as e:
                print(f"Error reading {path}: {e}")
    return None

filename = find_file()
if filename is None:
    print("unknown file")
    os.exit(-1)

def find_list():
    lists = os.path.join(bench_dir, "lists")
    for dirname in os.listdir(lists):
        if dirname == "all":
            continue
        d = os.path.join(lists, dirname)
        with open(d, "r") as f:
            s = f.read()
        if filename in s:
            return dirname
    return None

listname = find_list()
if listname is None:
    listname = "list not found"

m = re.search(r'_(\d{3})(?=\.smt2$)', filename)
number = m.group(1) if m else None

filename = re.sub(r'_(\d{3})(?=\.smt2$)', '', filename)


print(f"{listname}, {filename}, {number}")





