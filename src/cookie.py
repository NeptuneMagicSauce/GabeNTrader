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

        # TODO filter the sqlite query
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            shutil.copy(path, tmp.name)
            db = sqlite3.connect(tmp.name)
            mozdb = db.execute("select * from moz_cookies").fetchall()
            # db.execute(".mode column")
            # db.execute(".headers on")
            #  where domain="steamcommunity.com"
            for i in db.execute('select value from moz_cookies where host="steamcommunity.com" and name="steamLoginSecure" and originAttributes=""').fetchall():
                # print(str(i) + "\n")
                print(i[0])

        if mozdb is None:
            raise Exception("failed to database the cookie")

        for m in mozdb:
            # 1 : partitionKey
            # 2 : key
            # 3 : value
            # 4 : domain
            if len(m) >= 5 and m[1] == "" and m[2] == k_cookie_key and m[4] == k_web_domain:
                # print(m)
                cookie = str(m[3])
                # print(cookie)
                return { "steamLoginSecure": cookie }
    except Exception as e:
        print(e)
    return ""
