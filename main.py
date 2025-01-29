#!/usr/bin/env python3

import requests
import json
import pickle
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(os.path.realpath(__file__)))) # chdir to main.py
sys.path.append("src")

from cookie import *
from utils import *
from network import *

# import pandas as pd
# import numpy as np
# import scipy.stats as sci
# import matplotlib.pyplot as plt
# import seaborn as sns

k_app_name = "GabeNTrader"
k_game_id = "730"
k_link_to_latest = 'latest.items.json'

def GetItems():
    print("Getting item count", end='', file=sys.stderr)
    sys.stderr.flush()
    item_count_req = fetcher.get("https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid="+k_game_id+"&norender=1&count=1") # get page
    print('', file=sys.stderr)

    if not fetcher.check(item_count_req):
        exit(1)

    item_count_json = json.loads(item_count_req.content)

    if not 'total_count' in item_count_json:
        print('total_count not found', file=sys.stderr)
        return

    item_count = item_count_json['total_count'] # get total count
    # item_count = min(item_count, 2500)

    k_item_per_req = 100
    # k_item_per_req = 2

    item_names = []
    items = []

    print('Getting', item_count, 'items')
    progress = ProgressBar(item_count)

    index = 0

    link_to_latest_realpath = os.path.realpath(k_link_to_latest) if os.path.isfile(k_link_to_latest) else ""

    while index < item_count:
        data_file = str(k_game_id) + '_items_' + f"{index:06}" + '.json'
        if os.path.isfile(data_file):
            # TODO progress bar only for left to download
            # TODO remove partial data
            # with "if latest.link exists, load from here and carry on"
            # with error path for latest.link does not exist but data exists
            # TODO load faster with pickle
            # TODO compress data (maybe)
            is_the_last = len(link_to_latest_realpath) and os.path.realpath(data_file) == link_to_latest_realpath
            if not is_the_last and index + k_item_per_req >= item_count:
                is_the_last = True
            if is_the_last:
                items = json.load(open(data_file, 'r'))
            progress.tick(min(item_count, index + k_item_per_req))
            index += k_item_per_req
            continue

        while True:
            items_query = fetcher.get('https://steamcommunity.com/market/search/render/?start='+str(index)+'&search_descriptions=0&sort_column=default&sort_dir=desc&appid='+k_game_id+'&norender=1&count=' + str(k_item_per_req))

            if not fetcher.check(items_query):
                continue

            items_json = json.loads(items_query.content)

            if items_json is None:
                print("json parsing returned None", file=sys.stderr)
                continue
            if not 'results' in items_json:
                print("results not found:", file=sys.stderr)
                print(json.dumps(allItems, indent=1))
                continue

            break

        items_json = items_json['results'];

        count = len(items_json)

        if count == 0:
            print("results length = 0", file=sys.stderr)
            continue

        for item_json in items_json:
            item_names.append(item_json['hash_name'])
            items.append(item_json)

        print(json.dumps(items, indent=1), file=open(data_file,'w'))
        if os.path.isfile(k_link_to_latest):
            os.remove(k_link_to_latest)
        try:
            # this can fail on windows not developer-enabled
            os.symlink(data_file, k_link_to_latest)
        except Exception:
            pass

        progress.tick(index + count)
        index += count

    # uniqueness
    item_names = list(set(item_names))

    pickle.dump(item_names, open(k_game_id + '_item_names.pkl', "wb"))
    # with open(k_game_id + '_item_names.pkl', "rb") as file:
    #     item_names = pickle.load(file)
    # print("\n".join(item_names))
    # print(len(items), "items")

# def GetInventory():
#     print("fetch my inventory")
#     # request = requests.get("https://steamcommunity.com/market/&norender=1", cookies=cookie)
#     request = requests.get("https://steamcommunity.com/my/inventory/&norender=1")#, cookies=cookie)
#     print("returned", request.status_code)
#     print("request", request)
#     print("request.content", request.content)
#     as_json = json.loads(request.content)
#     json.dumps(as_json, indent=1)

############
### MAIN ###
############

init(k_app_name)

# TODO refresh cookie only periodically, pickle it
# because it's slow
# or refresh it if it fails
# also check if needs refreshing: either periodically or at every startup if fast
# cookie = GetCookie()
fetcher = Fetcher(GetCookie())

GetItems()

############
### TODO ###
############

# get.py prints to bat --json if present and if not piped
# alias bat --json
# test the cookie
# find userID from cookie
# list inventory
