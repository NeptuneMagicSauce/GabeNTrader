#!/usr/bin/env python3

import sqlite3
import subprocess
import tempfile
import os
import shutil

from utils import *

k_web_domain = "steamcommunity.com"
k_cookie_key = "steamLoginSecure"

def GetCookie():
    # gets the steamcommunity.com login cookie
    # supports Firefox on Windows WSL
    try:
        path = GetWindowsEnvVar("APPDATA")

        # WSL compatibility here
        path = ConvertPathToWSL(path)

        path = path + "/Mozilla/Firefox/Profiles/"

        latest_profile = None
        for profile in os.scandir(path):
            name = path + "/" + profile.name
            if latest_profile == None:
                latest_profile = name
                latest_time = profile.stat().st_mtime
            else:
                t = profile.stat().st_mtime
                if t > latest_time:
                    latest_time = t
                    latest_profile = name

        if latest_profile is None:
            raise Exception("no profiles in " + path)

        path = latest_profile + "/" + "cookies.sqlite"

        if not os.path.isfile(path):
            raise Exception("does not exist: " + path)

        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            shutil.copy(path, tmp.name)
            db = sqlite3.connect(tmp.name)
            # db.execute("select * from moz_cookies").fetchall()
            matches = db.execute('select value from moz_cookies where host="' + k_web_domain + '" and name="' + k_cookie_key + '" and originAttributes=""').fetchall()
            if len(matches) > 0:
                first_match = matches[0]
                if isinstance(first_match, tuple) and len(first_match) > 0:
                    cookie_value = first_match[0]
                    if isinstance(cookie_value, str):
                        return { k_cookie_key: cookie_value }
    except Exception as e:
        print(e)
    return ""
