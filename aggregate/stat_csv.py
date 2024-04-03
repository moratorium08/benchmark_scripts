#!/usr/bin/env python3
import sys
import json

# dataset identity
def ds_iden(x):
    l = x.split('/')
    if len(l) < 3:
        return x
    return '/'.join(l[-2:])

def cmpkey(x):
    return (ds_iden(x["file"]).split("/")[0], x["size"])

def max_preprocess(entries):
    mx = -1
    mx_cnt = None
    mx_name = None
    for (key, entry) in entries.items():
        time = float(entry["time"])
        cnt = int(entry["count"])
        if mx < time:
            mx = time
            mx_cnt = cnt
            mx_name = key
    return mx_name, mx_cnt, mx

def main():
    files = sys.argv[1:]

    if len(files) == 0:
        print('input json files as cli arguments')
        return

    filename = files[0]
    with open(filename, 'r') as f:
        data = json.load(f)

    ret = ""
    ca = 0
    wa = 0
    fail = 0
    wrong_answers = []
    ca_time_sum = 0
    data = sorted(data, key=cmpkey)
    for x in data:
        key = ds_iden(x['file'])
        target = 'invalid' if key.endswith('-e.in') or key.endswith('-e.ml.in') or key.endswith('-e.ml') else 'valid'
        ok = 1 if target == x['result'] else 0
        if ok == 1:
            ca += 1
            ca_time_sum += x['time']
        elif x['result'] == 'fail':
            fail += 1
        else:
            wa += 1
            wrong_answers.append(key)
        if "preprocess" in x:
            entries = x["preprocess"]
        else:
            print("warn: no preprocess")
            name = "dummy"
            cnt = -1
            time = -1
        name, cnt, time = max_preprocess(entries)
        ret += f"{key}, {x['time']}, {x['result']}, {ok}, {name}, {cnt}, {time}\n"

    with open('.'.join(filename.split('.')[:-1]) + '.csv', 'w') as f:
        f.write(ret)


    size = len(data)
    print("[stat]")
    print(f"Correct Answer: {ca} / {size}")
    print(f"Wrong Answer  : {wa} / {size}")
    print(f"Fail          : {fail} / {size}")
    if ca > 0:
      print(f"Correct Answer Response speed(mean): {ca_time_sum / ca}")

    print('Wrong Answers')
    for key in wrong_answers:
        print(f"- {key}")

main()
