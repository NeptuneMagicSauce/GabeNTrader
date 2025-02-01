import webview
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

    k_web_domain = "steamcommunity.com"
    k_cookie_key = "steamLoginSecure"

    def initialize():
        # gets the steamcommunity.com login cookie

        k_cookie_path = "cookie"
        try:
            Instances.cookie = pickle_load(k_cookie_path)
        except:
            # Instances.cookie = Cookie.get_cookie_firefox_installed_win32()
            Instances.cookie = Cookie.get_cookie_webview()
            if Instances.cookie is not None and len(Instances.cookie):
                # if cookie is not empty
                pickle_save(Instances.cookie, k_cookie_path)
        print('Cookie:', Instances.cookie['steamLoginSecure'][:50] + ' ...' if Instances.cookie is not None and len(Instances.cookie) else {})

    def get_cookie_firefox_installed_win32():
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

        try:
            db = sqlite_copy_db(path)
            cursor = db.con.execute('select value from moz_cookies where host="' + Cookie.k_web_domain + '" and name="' + Cookie.k_cookie_key + '"')
            first_match = cursor.fetchone()

            del(cursor) # otherwise it fails to delete file held by sqlite

            if first_match is not None and len(first_match):
                return { Cookie.k_cookie_key: first_match[0] }

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

    def get_cookie_webview():
        k_webview_storage = os.getcwd() + '/webview/' + OScompat.id_str
        # print('Storage:', k_webview_storage)
        def read_cookies(window):
            cookies = window.get_cookies()
            for c in cookies:
                for d in c.items():
                    # d is tuple, 0 is str key, 1 is morsel
                    print('StoredCookie:', d[0], '=', d[1].value)
        w = webview.create_window('', 'https://steamcommunity.com/login/home')
        webview.start(read_cookies, w, private_mode=False, storage_path=k_webview_storage)
