#!/bin/sh

if [ "$#" -le 3 ]; then
  echo "[Usage] $0 <solver_name> <n_threads> <timeout>"
  exit 1
fi

root=`dirname "${BASH_SOURCE[0]}"`/
cd $root

prefix="$1"
NTHREADS=$2
TIMEOUT=$3

echo "Target: $prefix"
echo "N Threads: $NTHRADS"
echo "Timeout: $TIMEOUT"

current_date=$(date +"%Y-%m-%d-%H")
filename="$prefix-$current_date.json"
csvname="$prefix-$current_date.csv"

mkdir -p results

python3 $prefix.py --n-threads=$NTHREADS comp_LIA-nonlin  --json results/comp_LIA-nonlin-$filename --timeout $TIMEOUT
python3 $prefix.py --n-threads=$NTHREADS comp_LIA-lin --json results/comp_LIA-lin-$filename --timeout $TIMEOUT

cd results
python3 ../../../slack-notify/slack_notify.py "manual benchmark" comp_LIA-nonlin-$filename comp_LIA-lin-$filename
