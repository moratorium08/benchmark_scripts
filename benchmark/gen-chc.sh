#!/bin/sh
set -eu

cwd=$(realpath "$(dirname "$0")")
INPUTS="$cwd/inputs"
LISTS="$cwd/lists"

rm -rf "$INPUTS" "$LISTS"
mkdir -p "$INPUTS" "$LISTS"

tmp_dir=$(mktemp -d -t hopdr-XXXX)
if [ $? -ne 0 ]; then
    echo "Error: Failed to create temporary directory."
    exit 1
fi

copy_and_list() {
    src_dir="$1"
    tgt_dir="$2"
    mkdir -p "$INPUTS/$tgt_dir"
    cp "$src_dir"/*.smt2 "$INPUTS/$tgt_dir" 2>/dev/null || true
    find "$INPUTS/$tgt_dir" -type f > "$LISTS/$tgt_dir"
    echo "$tgt_dir" >> "$INPUTS/.gitignore"
}

fetch_chc_benchmark() {
    repo_url="$1"
    commit_hash="$2"
    shift 2

    cd "$tmp_dir"
    git clone "$repo_url"
    repo_name=$(basename "$repo_url" .git)
    cd "$repo_name"
    git checkout "$commit_hash"
    find . -type f -name '*.gz' -exec gunzip {} +

    while [ $# -gt 1 ]; do
        src="$1"
        dest="$2"
        copy_and_list "$src" "$dest"
        shift 2
    done
}

fetch_recursive_plain_benchmark() {
    repo_url="$1"
    commit_hash="$2"
    dest_dir="$3"

    cd "$tmp_dir"
    git clone "$repo_url"
    repo_name=$(basename "$repo_url" .git)
    cd "$repo_name"
    git checkout "$commit_hash"

    repo_root=$(pwd)
    input_dest="$INPUTS/$dest_dir"

    find . -type f -name '*.smt2' | while read -r file; do
        rel_path=$(realpath --relative-to="$repo_root" "$file")
        dest_path="$input_dest/$rel_path"
        mkdir -p "$(dirname "$dest_path")"
        cp "$file" "$dest_path"
    done

    find "$input_dest" -type f > "$LISTS/$dest_dir"
    echo "$dest_dir" >> "$INPUTS/.gitignore"
}


# ADT instances
fetch_recursive_plain_benchmark \
  https://github.com/chc-comp/ADTRem \
  a7d395d81837bd95d62011f94a7ce11718321ead \
  ADTRem

fetch_recursive_plain_benchmark \
  https://github.com/chc-comp/adt-purified-benchmarks \
  47d1d74f13357c0ef122ed30bbe8b6904f1cdec9 \
  adt-purified

fetch_recursive_plain_benchmark \
  https://github.com/chc-comp/ringen-adt-benchmarks \
  413f3ee92f1c82f50ad9f2ad9408eaddf5eadb71 \
  ringen-adt

fetch_recursive_plain_benchmark \
  https://github.com/chc-comp/rust-horn \
  e5a86a1ad252fe1df75e06814769ec1d14540032 \
  rust-horn

fetch_recursive_plain_benchmark \
  https://github.com/chc-comp/tip-adt-lia \
  f085f5fb650dad1fd4e2ff4428db21bbfc8cd4ba \
  tip-adt-lia


# Format the instances
FORMAT_REPO="https://github.com/chc-comp/scripts"
cd "$tmp_dir"
git clone "$FORMAT_REPO"
FORMAT_SCRIPT="$tmp_dir/scripts/format/src/format.py"

for file in $(find "$INPUTS" -name '*.smt2'); do
    outdir=$(dirname "$file")_formatted
    mkdir -p "$outdir"

    # Run formatter and capture stdout+stderr
    output=$(python3 "$FORMAT_SCRIPT" --skip_errors True --out_dir "$outdir" "$file" 2>&1 || true)


    # Check if format.py failed or skipped this file
    if echo "$output" | grep -q "Skipping file"; then
        echo "[Warning] Format skipped for: $file" >&2
        rm -rf "$outdir"
        continue
    fi

    # Check if any output files were generated
    shopt -s nullglob
    formatted_files=("$outdir"/$(basename "${file%.smt2}")_*.smt2)
    shopt -u nullglob

    if [ ${#formatted_files[@]} -eq 0 ]; then
        echo "[Warning] No formatted output for: $file" >&2
        rm -rf "$outdir"
        continue
    fi

    # Replace original file with all formatted outputs
    rm "$file"
    for formatted in "${formatted_files[@]}"; do
        mv "$formatted" "$(dirname "$file")/$(basename "$formatted")"
    done

    rmdir "$outdir" 2>/dev/null || true
done



echo "Rebuilding file lists after formatting..."
> "$LISTS/all"
cd "$INPUTS"
for dir in $(find . -mindepth 1 -maxdepth 1 -type d); do
    listname=$(basename "$dir")
    find "$dir" -type f -name '*.smt2' > "$LISTS/$listname"
    cat "$LISTS/$listname" >> "$LISTS/all"
done


# CHC-COMP 

fetch_chc_benchmark \
  https://github.com/chc-comp/chc-comp24-benchmarks \
  1e8596fb798baafb55fb1a693afc31b12553d281 \
  LIA-Lin 24comp_LIA-Lin \
  LIA 24comp_LIA \
  ADT-LIA 24comp_ADT-LIA

fetch_chc_benchmark \
  https://github.com/chc-comp/chc-comp23-benchmarks \
  cca5a86a4939e406b714cb5a55f35a8a2f581a48 \
  LIA-nonlin comp_LIA-nonlin \
  LIA-lin comp_LIA-lin \
  ADT-LIA-nonlin comp_ADT-LIA-nonlin

fetch_chc_benchmark \
  https://github.com/chc-comp/chc-comp22-benchmarks \
  497725c7c994cc06f74a8933ec292fa03a66ad48 \
  ADT-NONLIN 22comp_ADT-LIA

