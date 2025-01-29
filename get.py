#!/usr/bin/env python3

import requests
import json
import sys
import shutil
import os
import subprocess
import tempfile

# todo option no-cookie

sys.path.append(os.path.dirname(os.path.abspath(os.path.realpath(__file__))) + "/src")
from cookie import *
from network import *

cookie = GetCookie()

if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "url_to_fetch")
    exit(1)
url = sys.argv[1]

req = requests.get(url, cookies=cookie)

if not Fetcher.check(req):
    exit(1)

if len(req.content) <= 0:
    print("content length zero")
    exit(1)

try:
    as_json = json.loads(req.content)
except Exception as e:
    print("did not parse JSON:", req.content)
    exit(1)

as_string = json.dumps(as_json, indent=1)

if sys.stdout.isatty() and shutil.which("batcat"):
    with tempfile.NamedTemporaryFile(delete_on_close=False) as tmp:
        tmp.close()
        print(as_string, file=open(tmp.name, 'w'))
        subprocess.run([ "batcat", "-l", "json", "--theme", "Monokai Extended", "--file-name", url, tmp.name])
else:
    print(as_string)
