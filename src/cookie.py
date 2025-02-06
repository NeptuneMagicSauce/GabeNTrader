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
from gui import *

class Cookie:

    k_web_domain = "steamcommunity.com"
    k_cookie_key = "steamLoginSecure"
    k_cookie_path = "cookie.pkl"

    def initialize():
        # gets the steamcommunity.com login cookie

        try:
            Instances.cookie = pickle_load(Cookie.k_cookie_path)
        except:
            # Instances.cookie = Cookie.get_cookie_firefox_installed_win32()
            Instances.cookie = Cookie.get_cookie_webview().get()
            if len(Instances.cookie):
                # if cookie is not empty
                pickle_save(Instances.cookie, Cookie.k_cookie_path, compress=False)
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
        def print_is_valid():
            print('CookieIsValid:', Instances.cookie_is_valid)
        print_is_valid()
        if not Instances.cookie_is_valid and len(Instances.cookie):
            # if cookie not valid
            # and cookie could be retrieved
            try:
                # invalidate in cache
                os.remove(Cookie.k_cookie_path)
            except:
                pass
            Cookie.initialize() # refresh the cookie
            Network.initialize() # consume the new cookie
            Steam.initialize() # re-validate the new cookie
            print_is_valid()

    class get_cookie_webview:
        # needs to be a class to share data between threads

        def sleep(self):
            time.sleep(0.05)

        def get(self):
            k_expect_slow_start = True if OScompat.id == OScompat.ID.WSL else False
            k_support_hidden_start = False if OScompat.id == OScompat.ID.WSL else True

            if k_expect_slow_start:
                print('Getting the login information ...', flush=True)

            self.cookie_value = ''
            self.k_url = 'https://steamcommunity.com/login/home'
            self.window = webview.create_window('', self.k_url, hidden=k_support_hidden_start, height=800)
            self.is_running = True # needed on WSL for thread termination

            def find_cookie():
                # ! not the main thread, it's the webview thread
                threading.current_thread().name = 'FindCookie'
                # print('>>>')
                while self.is_running:
                    if self.window is None:
                        # this webview was closed
                        # or we're called too early
                        self.sleep()
                        continue

                    try:
                        url = self.window.get_current_url()
                    except Exception as e:
                        print('get_url failed:', e)
                        self.sleep()
                        continue

                    if url is None:
                        continue

                    # restrict to the unique url
                    if not url == self.k_url:
                        self.window.load_url(self.k_url)

                    try:
                        cookies = self.window.get_cookies()
                    except Exception as e:
                        print('get_cookies failed:', e)
                        self.sleep()
                        continue

                    # cookie.items() is dict_items
                    # item is tuple, 0 is str key, 1 is morsel

                    if cookies is None:
                        self.sleep()
                        continue

                    if cookie := next(filter(lambda c:
                                             list(c.items())[0][0] == Cookie.k_cookie_key, cookies), None):
                        self.cookie_value = list(cookie.items())[0][1].value
                        # if window is hidden (on first launch)
                        # we must quit the webview before returning
                        # otherwise we're stuck
                        # and if window is not hidden we also want to destroy it
                        self.window.destroy()

                    # here we did not find the cookie in storage
                    # so we show the window for logging-in
                    self.window.show() # no effect on WSL, which is why it started not hidden
                    self.sleep()

                # print('<<<')

            self.window.events.shown += find_cookie

            # pywebview mut be run on main thread = gui thread
            GUI.wait_for_load()
            GUI.app.start_webview.emit()
            GUI.app.webview_finished.wait()

            self.is_running = False

            if not len(self.cookie_value):
                return {}

            return { Cookie.k_cookie_key: self.cookie_value }
