import sqlite3
import subprocess
import tempfile
import os
import shutil

from instances import *
from utils import *
from network import *
from steam import *

class Cookie:

    def initialize():
        # gets the steamcommunity.com login cookie

        k_cookie_path = "cookie"
        try:
            Instances.cookie = pickle_load(k_cookie_path)
        except:
            Instances.cookie = Cookie.get_cookie_firefox_win32()
            if len(Instances.cookie):
                # if cookie is not empty
                pickle_save(Instances.cookie, k_cookie_path)
        print('Cookie:', Instances.cookie['steamLoginSecure'][:50] + ' ...' if len(Instances.cookie) else {})

    def get_cookie_firefox_win32():
        # supports Firefox on Windows WSL

        try:
            path = get_firefox_dir()

            latest_profile = None
            for profile in os.scandir(path):
                name = path + "/" + profile.name
                if not os.path.isdir(name):
                    continue
                if latest_profile == None:
                    latest_profile = name
                    latest_time = profile.stat().st_mtime
                else:
                    t = profile.stat().st_mtime
                    if t > latest_time:
                        latest_time = t
                        latest_profile = name

            if latest_profile is None:
                print("no profiles in", path)
                return {}

            path = latest_profile + "/" + "cookies.sqlite"

            if not os.path.isfile(path):
                print("not a file:", path)
                return {}

            return Cookie.get_cookie_from_file(path)
        except Exception as e:
            print(e)
            return {}

    def get_cookie_from_file(path):

        k_web_domain = "steamcommunity.com"
        k_cookie_key = "steamLoginSecure"
        try:
            db = sqlite_copy_db(path)
            cursor = db.con.execute('select value from moz_cookies where host="' + k_web_domain + '" and name="' + k_cookie_key + '"')
            first_match = cursor.fetchone()

            del(cursor) # otherwise it fails to delete file held by sqlite

            if first_match is not None and len(first_match):
                return { k_cookie_key: first_match[0] }

            print('failed to find cookie with sqlite')
        except Exception as e:
            print(e)
        return {}

    def refresh_cookie_if_invalid():
        print('CookieIsValid:', Instances.cookie_is_valid)
        if not Instances.cookie_is_valid and len(Instances.cookie):
            # if cookie not valid
            # and cookie could be retrieved
            Cookie.initialize() # refresh the cookie
            Network.initialize() # consume the new cookie
            Steam.initialize() # re-validate the new cookie
