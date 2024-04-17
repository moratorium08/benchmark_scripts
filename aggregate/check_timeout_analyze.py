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
    n_fail_hoice = 0
    n_execute = 0
    no_safety = 0
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
        pre_hoice = get_time(entries, "preprocess by hoice")
        n_pre_hoice = get_count(entries, "preprocess by hoice")
        safety_count = get_count(entries, "safety")
        der_count = get_count(entries, "remove tmp var")

        check_entries = x.get("check", {})
        execute = get_time(check_entries, "execute")
        cnt_execute = get_count(check_entries, "execute")

        if check_entries == {}:
            n_no_check += 1
            if n_pre_hoice > 0 and safety_count > 0:
                print(x["preprocess"])
        # 0 means, reached but not finished?
        if nparse == 0:
            n_fail_parse += 1
        if n_pre_hoice == 0:
            n_fail_hoice += 1
            print(f"- {x['file']}")
            print("  - parse_chc:", get_time(entries, "parse_chc"))
        print(safety_count)
        if safety_count == -1:
            no_safety += 1
        if cnt_execute != 1:
            n_execute += 1

        ret += f"{key}, {x['time']}, {x['result']}, {parse}, {pre_hoice}, {preprocess}, {execute}\n"
    header = "filename, time, result, ok, pparse, hoice preprocess, preprocess, execute\n"

    with open('.'.join(filename.split('.')[:-1]) + '.csv', 'w') as f:
        f.write(header)
        f.write(ret)

    size = len(data)
    print("[stat]")
    print(f"n Invalids    : {invalid} / {size}")
    print(f"Fail          : {fail} / {size}")
    print(f"-------------  ")
    print(f"N Parse fail  : {n_fail_parse} / {size}")
    print(f"N Hoice Pre   : {n_fail_hoice} / {size}")
    print(f"No Safety     : {no_safety} / {size}")
    print(f"No Check      : {n_no_check} / {size}")
    print(f"No Execute     : {n_execute} / {size}")


main()
