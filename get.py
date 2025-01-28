#!/usr/bin/env python3

import requests
import json
import sys

from main import GetCookie

cookie = GetCookie()

if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "url_to_fetch")
    exit(1)
url = sys.argv[1]

req = requests.get(url, cookies=cookie)

if req.status_code != 200:
    print(req.reason)
    exit(1)

if len(req.content) <= 0:
    print("content length zero")
    exit(1)

try:
    as_json = json.loads(req.content)
except Exception as e:
    print("did not parse JSON:", req.content)
    exit(1)

print(json.dumps(as_json, indent=1))
