#!/usr/bin/env python3

import requests
import json
import pickle

from instances import *
from utils import *
from gui import *

# class Data:
k_game_id = "730"

def get_items():

    items = []
    index = 0

    cache_path = "items.pkl"
    try:
        items = pickle_load(cache_path)
        items = items[:len(items)-300] # debug: refresh last 3 chunks
        index = len(items)
        print("InCache:", index)
    except:
        print("Failed to load cache from " + cache_path)

    item_count_json = Instances.fetcher.get_json("https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid="+k_game_id+"&norender=1&count=1")

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

    # ProgressBar is not compatible with safe multithreaded print
    to_fetch = item_count - index
    # progress = ProgressBar(to_fetch, size=40)
    fetched = 0
    GUI.app.tick_progress.emit(0, 1, 'Downloading Foo')

    while index < item_count:
        items_json = Instances.fetcher.get_json("https://steamcommunity.com/market/search/render/?start=" + str(index) + "&search_descriptions=0&sort_column=default&sort_dir=desc&appid=" + k_game_id + "&norender=1&count=" + str(k_item_per_req))

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
        # progress.tick(fetched)
        GUI.app.tick_progress.emit(fetched, to_fetch, '')

    GUI.app.tick_progress.emit(0, 0, '')

    pickle_save(items, cache_path)

    # for i in range(0, 10):
        # print(items[i]['asset_description']['icon_url'])

    # extract hash_name
    names = set()
    for i in items:
        names.add(i['hash_name'])
    pickle_save(names, "names.pkl")

    print("Loaded:", len(items))
    print("Names:", len(names))

# def get_inventory():
#     print("fetch my inventory")
#     # request = requests.get("https://steamcommunity.com/market/&norender=1", cookies=cookie)
#     request = requests.get("https://steamcommunity.com/my/inventory/&norender=1")#, cookies=cookie)
#     print("returned", request.status_code)
#     print("request", request)
#     print("request.content", request.content)
#     as_json = json.loads(request.content)
#     json.dumps(as_json, indent=1)
