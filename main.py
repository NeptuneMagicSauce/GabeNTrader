#!/usr/bin/env python3

import os
import sys

# find library files in /src like this:
sys.path.append(os.path.dirname(os.path.abspath(os.path.realpath(__file__))) + '/src')

from instances import *
from cookie import *
from utils import *
from network import *
from steam import *
from data import *

# import pandas as pd
# import numpy as np
# import scipy.stats as sci
# import matplotlib.pyplot as plt
# import seaborn as sns


############
### MAIN ###
############

Utils.initialize("GabeNTrader")

Cookie.initialize()

Network.initialize()

Steam.initialize()

Cookie.refresh_cookie_if_invalid()

if not Instances.cookie_is_valid:
    print('no valid cookie, exiting')
    exit(1)

Steam.get_user_name()

get_items()
