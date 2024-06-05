import requests
import os
import sys
import json

if len(sys.argv) < 2:
    print("python3 slack_notify.py <message> json_files...")
    sys.exit(1)

message = sys.argv[1]
filenames = sys.argv[2:]

token = os.environ["SLACK_TOKEN"]
channel_id = 'C04S69J560K'

url = "https://slack.com/api/chat.postMessage"

headers = {
    "Authorization": "Bearer {}".format(token),
    "Content-Type": "application/json"
}


def summarize(filename):
    nvalid = 0
    ninvalid = 0
    nfail = 0
    with open(filename) as f:
        results = json.load(f)
    # for bench version 2
    if type(results) != list:
        results = results["result"]
    for r in results:
        if r["result"] == "valid":
            nvalid += 1
        elif r["result"] == "invalid":
            ninvalid += 1
        else:
            nfail += 1
    return nvalid, ninvalid, nfail


fields = []
for f in filenames:
    (nvalid, ninvalid, nfail) = summarize(f)
    body = f"{nvalid} valids, {ninvalid} invalids, {nfail} fail"
    title = f.split(".")[0]
    obj = {
        "title": title,
        "value": body,
        "short": True
    }
    fields.append(obj)

attachments = [
    {
        "mrkdwn_in": ["text"],
        # "pretext": "Here is ",
        # "author_name": "",
        # "author_link": "http://flickr.com/bobby/",
        # "author_icon": "https://placeimg.com/16/16/people",
        "title": "Benchmark Results",
        # "title_link": "https://api.slack.com/",
        # "text": message,
        "fields": fields
        # "thumb_url": "http://placekitten.com/g/200/200",
        # "footer": "footer",
        # "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
        # "ts": 123456789
    }
]


data = {
    "channel": channel_id,
    "text": ":white_check_mark: Benchmark finished\n"+message,
    "attachments": attachments
}

response = requests.post(url, headers=headers, json=data)
print(response.text)
