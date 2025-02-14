import time
import webview
import sqlite3
import subprocess
import tempfile
import os
import shutil
import multiprocessing

from instances import *
from utils import *
from network import *
from steam import *
from gui import *

class Cookie:

    class Signals(QObject):
        show_login = pyqtSignal()

    signals = Signals()

    k_web_domain = "steamcommunity.com"
    k_cookie_key = "steamLoginSecure"
    k_cookie_path = "cookie.pkl"

    def initialize():
        # gets the steamcommunity.com login cookie

        # GUI.wait_for_ready() NO! we dont want to wait for background data load
        # GUI.app.status_bar.login.set_text.emit('foo')

        try:
            print('Debug Remove this')
            raise
            Instances.cookie = pickle_load(Cookie.k_cookie_path)
        except:
            # Instances.cookie = Cookie.get_from_installed_browser()
            # Instances.cookie = Cookie.webview.get_on_main_thread()
            Instances.cookie = Cookie.webview.get_on_subprocess()

            Cookie.signals.show_login.emit()

            if len(Instances.cookie):
                # if cookie is not empty
                pickle_save(Instances.cookie, Cookie.k_cookie_path, compress=False)
        print('Cookie:', Instances.cookie['steamLoginSecure'][:50] + ' ...' if Instances.cookie is not None and len(Instances.cookie) else {})

    def get_from_installed_browser():
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

            return Cookie.get_from_browser_sqlite(path)
        except Exception as e:
            print(e)
            return {}

    def get_from_browser_sqlite(path):

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

    class webview:
        cookie_value = ''

        class Parallelism(Enum):
            Thread = 0
            Process = 1

        def get_on_subprocess():
            parent, child = multiprocessing.Pipe()
            p = multiprocessing.Process(target=Cookie.webview.retrieve, args=(Cookie.webview.Parallelism.Process, child,))
            p.start()
            ret = parent.recv()
            # p.join() # not needed
            return ret

        def get_on_main_thread():
            return Cookie.webview.retrieve(Cookie.webview.Parallelism.Thread)

        def retrieve(parallelism, pipe=None):

            k_expect_slow_start = True if OScompat.id == OScompat.ID.WSL else False
            k_support_hidden_start = False if OScompat.id == OScompat.ID.WSL else True
            k_webview_storage = os.getcwd() + '/webview/' + OScompat.id_str

            if k_expect_slow_start:
                print('Getting the login information ...', flush=True)

            k_url = 'https://steamcommunity.com/login/home'
            window = webview.create_window('', k_url, hidden=k_support_hidden_start, height=800)
            is_running = True # needed on WSL for thread termination

            def find_cookie():
                def sleep():
                    time.sleep(0.05)

                # ! not the main thread, it's the webview sub-thread
                threading.current_thread().name = 'FindCookie'
                # print('>>>')
                while is_running:
                    if window is None:
                        # this webview was closed
                        # or we're called too early
                        sleep()
                        continue

                    try:
                        url = window.get_current_url()
                    except Exception as e:
                        print('get_url failed:', e)
                        sleep()
                        continue

                    if url is None:
                        continue

                    # restrict to the unique url
                    if not url == k_url:
                        window.load_url(k_url)

                    try:
                        cookies = window.get_cookies()
                    except Exception as e:
                        print('get_cookies failed:', e)
                        sleep()
                        continue

                    # cookie.items() is dict_items
                    # item is tuple, 0 is str key, 1 is morsel

                    if cookies is None:
                        sleep()
                        continue

                    if cookie := next(filter(lambda c:
                                             list(c.items())[0][0] == Cookie.k_cookie_key, cookies), None):
                        Cookie.webview.cookie_value = list(cookie.items())[0][1].value
                        # if window is hidden (on first launch)
                        # we must quit the webview before returning
                        # otherwise we're stuck
                        # and if window is not hidden we also want to destroy it
                        window.destroy()

                    # here we did not find the cookie in storage
                    # so we show the window for logging-in
                    window.show() # no effect on WSL, which is why it started not hidden
                    sleep()

                # print('<<<')

            window.events.shown += find_cookie

            match parallelism:
                case Cookie.webview.Parallelism.Thread:
                    # signal qt main thread to start
                    # because it must be run on main thread
                    GUI.wait_for_ready()
                    GUI.app.start_webview.emit(k_webview_storage)
                    GUI.app.webview_finished.wait()
                case Cookie.webview.Parallelism.Process:
                    # direct start, we are not blocking the gui process
                    webview.start(private_mode=False, storage_path=k_webview_storage)

            is_running = False # so that the thread find_cookie finishes if webview closed and not found

            ret = {}
            if len(Cookie.webview.cookie_value):
                ret[Cookie.k_cookie_key] = Cookie.webview.cookie_value

            if pipe:
                pipe.send(ret)

            return ret
