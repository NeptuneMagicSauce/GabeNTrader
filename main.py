#!/usr/bin/env python3

import os
import sys
import threading

# find library files in /src like this:
sys.path.append(os.path.dirname(os.path.abspath(os.path.realpath(__file__))) + '/src')

from instances import *
from cookie import *
from utils import *
from network import *
from steam import *
from data import *
from gui import *
from remoteimages import *

# import pandas as pd
# import numpy as np
# import scipy.stats as sci
# import matplotlib.pyplot as plt
# import seaborn as sns

############
### MAIN ###
############

def initialize():

    Cookie.initialize()

    Network.initialize()

    Images.initialize()

    # first request gets user_id
    # and checks cookie is valid
    Steam.initialize()

    Cookie.refresh_cookie_if_invalid()

    if not Instances.cookie_is_valid:
        return

    # second request gets user_name, third request gets user_icon
    Steam.get_user_name()

    get_items()

    print('Load finished')

# subprocesses: will execute what's before main
# and will not execute main
Utils.initialize("GabeNTrader")

if __name__ == '__main__':

    Instances.is_main_process = True

    # initialize gui: it must be ready to not miss signals before other threads are spawned
    # important signals that can not be missed: central.login.show, tool_bar.user_action.found
    app = GUI.App()
    app.initialize()

    # connect signals
    Utils.printer.event.connect(app.print_console_cb)
    Steam.signals.login_validated.connect(app.status_bar.login.set_success)
    Steam.signals.user_id_found.connect(app.tool_bar.user_action.found)
    Cookie.signals.show_login.connect(app.central.login.show)
    Cookie.signals.show_login_old.connect(app.start_webview_cb)
    Data.signals.tick_progress.connect(app.tick_progress)

    # initialize initial load thread
    threading.Thread(target=initialize, name='Init').start()

    app.run()
    exit(GUI.return_code)
