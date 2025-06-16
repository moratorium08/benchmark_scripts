#!/usr/bin/env python3
import os
import sys
import argparse
import difflib
import json

def compute_diff_lines(a_lines, b_lines, fromfile, tofile):
    """
    Extract only added/removed lines (+/-) from unified_diff and return as string.
    """
    diff = difflib.unified_diff(
        a_lines, b_lines,
        fromfile=fromfile, tofile=tofile,
        lineterm=''
    )
    filtered = []
    for line in diff:
        if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
            continue
        if line.startswith('+') or line.startswith('-'):
            filtered.append(line)
    return '\n'.join(filtered), sum(1 for l in filtered)

def find_best_matches(target_lines, bench_root, rel_root):
    """
    Search recursively under bench_root and return files with the smallest diff to target_lines.
    Each result is a tuple: (relative path, diff string)
    """
    min_diff = None
    best_matches = []
    for root, _, files in os.walk(bench_root):
        for fname in files:
            path = os.path.join(root, fname)
            try:
                with open(path, 'r') as f:
                    b_lines = f.readlines()
            except Exception as e:
                print(f"Warning: failed to read {path}: {e}", file=sys.stderr)
                continue

            diff_text, diff_count = compute_diff_lines(
                target_lines, b_lines,
                fromfile='target', tofile=fname
            )

            if min_diff is None or diff_count < min_diff:
                min_diff = diff_count
                best_matches = [(os.path.relpath(path, rel_root), diff_text)]
            elif diff_count == min_diff:
                best_matches.append((os.path.relpath(path, rel_root), diff_text))

    return best_matches

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_bench = os.path.join(script_dir, "../benchmark/inputs/25-adt-chc-comp")
    parser = argparse.ArgumentParser(
        description="For each formatted file, find the most similar original file (minimum diff) from benchmark inputs and output results as JSON."
    )
    parser.add_argument(
        'formatted_dir',
        help="Directory containing formatted SMT2 files"
    )
    parser.add_argument(
        '--benchmark', '-b',
        default=default_bench,
        help="Benchmark root directory (default: %(default)s)"
    )
    args = parser.parse_args()

    bench_inputs = args.benchmark
    if not os.path.isdir(bench_inputs):
        print(f"Error: Benchmark input directory not found: {bench_inputs}", file=sys.stderr)
        sys.exit(1)

    results = []

    for fname in sorted(os.listdir(args.formatted_dir)):
        print(fname, file=sys.stderr)
        fpath = os.path.join(args.formatted_dir, fname)
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, 'r') as f:
                target_lines = f.readlines()
        except Exception as e:
            print(f"Warning: failed to read {fpath}: {e}", file=sys.stderr)
            continue

        best_matches = find_best_matches(
            target_lines,
            bench_root=bench_inputs,
            rel_root=bench_inputs
        )

        entry = {
            "name": fname,
            "most-relevant": []
        }
        for relpath, diff_text in best_matches:
            item = {"name": relpath}
            if diff_text:
                item["diff"] = diff_text
            entry["most-relevant"].append(item)

        results.append(entry)

    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()

