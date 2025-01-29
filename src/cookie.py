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
        for profile in os.listdir(path):
            profile = path + "/" + profile
            if latest_profile == None:
                latest_profile = profile
                latest_time = os.path.getmtime(profile)
            else:
                t = os.path.getmtime(profile)
                if t > latest_time:
                    latest_time = t
                    latest_profile = profile

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
                # print(str(matches[0]))
                return { k_cookie_key: str(matches[0]) }
    except Exception as e:
        print(e)
    return ""
