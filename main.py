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
from steam import *

# import pandas as pd
# import numpy as np
# import scipy.stats as sci
# import matplotlib.pyplot as plt
# import seaborn as sns

k_app_name = "GabeNTrader"
k_game_id = "730"
k_link_to_latest = 'latest.items.json'

def GetItems():

    items = []
    index = 0

    cache_path = "items.pkl"
    try:
        items = pickle_load(cache_path) #pickle.load(open(cache_path, 'rb'))
        index = len(items)
        print("InCache:", index)
    except:
        print("Failed to load cache from " + cache_path)

    item_count_json = fetcher.get_json("https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid="+k_game_id+"&norender=1&count=1")

    if item_count_json is None:
        exit(1)

    if not 'total_count' in item_count_json:
        print('total_count not found')
        return

    item_count = item_count_json['total_count'] # get total count
    # item_count = min(item_count, 14000)
    # item_count = 500

    print("MarketItems:", item_count)

    k_item_per_req = 100
    # k_item_per_req = 2

    progress = ProgressBar(item_count - index)
    fetched = 0

    while index < item_count:

        items_json = fetcher.get_json("https://steamcommunity.com/market/search/render/?start=" + str(index) + "&search_descriptions=0&sort_column=default&sort_dir=desc&appid=" + k_game_id + "&norender=1&count=" + str(k_item_per_req))

        if items_json is None:
            print("json parsing returned None")
            break

        if not 'results' in items_json:
            print("'results' not found:")
            print(json.dumps(allItems, indent=1))
            break

        items_json = items_json['results'];

        count = len(items_json)

        if count == 0:
            print("results length = 0")
            break

        items.extend(items_json)

        fetched += count
        index += count
        progress.tick(fetched)

    pickle_save(items, cache_path)

    # extract hash_name
    names = set()
    for i in items:
        names.add(i['hash_name'])
    pickle_save(names, "names.pkl")

    print("Loaded:", len(items))
    print("Names:", len(names))

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
fetcher.initialize(GetCookie())

# GetItems()
id = GetUserId()
print(id)

# TODO test the cookie, it must load the private inventory
# TODO invalidate cache if total_count change
# needs valid cookie for TooManyRequests
# needs another serialized bit: is pickle finished?
# because cache size can not be compared without that
# TODO refresh cookie only if needed, pickle it
# but only if we have a reliable way to validate it
# TODO find userID from cookie
# TODO list inventory
