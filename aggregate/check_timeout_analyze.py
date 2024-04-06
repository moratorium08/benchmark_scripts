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


def get_time(e, key):
    if key not in e:
        # print(key, e)
        return -1
    return float(e[key]["time"])


def get_count(e, key):
    if key not in e:
        return -1
    return float(e[key]["count"])


def main():
    files = sys.argv[1:]

    if len(files) == 0:
        print('input json files as cli arguments')
        return

    filename = files[0]
    with open(filename, 'r') as f:
        data = json.load(f)

    ret = ""
    invalid = 0
    fail = 0
    n_no_check = 0
    n_fail_parse = 0
    data = sorted(data, key=cmpkey)
    for x in data:
        key = ds_iden(x['file'])
        # print(key)
        if x['result'] == 'invalid':
            invalid += 1
        elif x['result'] == 'fail':
            fail += 1
        entries = x.get("preprocess", {})
        preprocess = get_time(entries, "overall")
        parse = get_time(entries, "parse_chc")
        nparse = get_count(entries, "parse_chc")

        entries = x.get("check", {})
        execute = get_time(entries, "execute")

        if entries == {}:
            n_no_check += 1
            print(x)
        if nparse == 0:
            n_fail_parse += 1

        ret += f"{key}, {x['time']}, {x['result']}, {preprocess}, {parse}, {execute}\n"
    header = "filename, time, result, ok, preprocess, parse, execute\n"

    with open('.'.join(filename.split('.')[:-1]) + '.csv', 'w') as f:
        f.write(header)
        f.write(ret)

    size = len(data)
    print("[stat]")
    print(f"n Invalids    : {invalid} / {size}")
    print(f"Fail          : {fail} / {size}")
    print(f"N Parse fail  : {n_fail_parse} / {size}")
    print(f"N No Check    : {n_no_check} / {size}")


main()
