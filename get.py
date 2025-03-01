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

Utils.initialize('GabeNTrader')
Cookie.initialize()

if len(sys.argv) != 2:
    builtins.print("Usage:", sys.argv[0], "url_to_fetch")
    exit(1)
url = sys.argv[1]

req = requests.get(url, cookies=Instances.cookie) #cookie)

if not Fetcher.check(req):
    exit(1)

if len(req.content) <= 0:
    builtins.print("content length zero")
    exit(1)

try:
    as_json = json.loads(req.content)
except Exception as e:
    builtins.print("did not parse JSON", file=sys.stderr)
    builtins.print(req.text)
    exit(1)

as_string = json.dumps(as_json, indent=1)

if sys.stdout.isatty() and shutil.which("batcat"):
    with tempfile.NamedTemporaryFile(delete_on_close=False) as tmp:
        tmp.close()
        builtins.print(as_string, file=open(tmp.name, 'w'))
        subprocess.run([ "batcat", "-l", "json", "--theme", "Monokai Extended", "--file-name", url, tmp.name])
else:
    builtins.print(as_string)
