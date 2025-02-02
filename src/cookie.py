import time
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
            Instances.cookie = Cookie.get_cookie_webview().get()
            if len(Instances.cookie):
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

    class get_cookie_webview:
        # needs to be a class to share data between threads

        def get(self):
            k_webview_storage = os.getcwd() + '/webview/' + OScompat.id_str
            # print('Storage:', k_webview_storage)

            self.cookie_value = ''
            self.window = webview.create_window('', 'https://steamcommunity.com/login/home',
                                                hidden=True, height=800)

            def find_cookie(window):
                # ! not the main thread, it's the webview thread

                while True:
                    if window is None:
                        # this webview was closed
                        break

                    cookies = window.get_cookies()
                    # cookie.items() is dict_items
                    # item is tuple, 0 is str key, 1 is morsel

                    if cookies is None:
                        break

                    if cookie := next(filter(lambda c:
                                             list(c.items())[0][0] == Cookie.k_cookie_key, cookies), None):
                        self.cookie_value = list(cookie.items())[0][1].value
                        # if window is hidden (on first launch)
                        # we must quit the webview before returning
                        # otherwise we're stuck
                        self.window.destroy()
                        return

                    window.show()
                    time.sleep(0.5)

            webview.start(find_cookie, self.window, private_mode=False, storage_path=k_webview_storage)

            if not len(self.cookie_value):
                return {}

            return { Cookie.k_cookie_key: self.cookie_value }
