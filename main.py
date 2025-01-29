#!/usr/bin/env python3

import requests
import json
import pickle
import os
import time
import random
import sys

from cookie import GetCookie

# import pandas as pd
# import numpy as np
# import scipy.stats as sci
# import matplotlib.pyplot as plt
# import seaborn as sns

random.seed(time.time())

k_game_id = "730"
k_data_dir = "data"
k_link_to_latest = 'latest.items.json'

# TODO move all classes and functions in files

class RateLimiter:
    def __init__(self, period):
        self.period = period
        self.last_time = float(-1)
    def tick(self):
        current_time = time.time()
        if self.last_time <= 0:
            elapsed = float(0)
            to_wait = float(0)
        else:
            elapsed = current_time - self.last_time
            to_wait = max(0.0, self.period - elapsed)
        time.sleep(to_wait)
        self.last_time = time.time()

class Fetcher(RateLimiter):
    def __init__(self):
        super().__init__(period=2.5)
                         # 10.0)
                         #3.0)
                         # 2.5)
    def get(self, url):
        self.tick()
        ret = requests.get(url, cookies=cookie)

        with open('.latest.code', 'w') as c, open('.latest.json', 'w') as j, open('.latest.url', 'w') as u:
            print(ret.status_code, file=c)
            print(ret.url, file=u)
            if ret.status_code == requests.codes.ok:
                # print(ret.json(), file=j) # requests.json() fails to parse with jq
                print(json.dumps(json.loads(ret.content), indent=1), file=j)
            else:
                print('', file=j)
        return ret
    def check(self, request):
        if request.status_code != requests.codes.ok:
            print(request.status_code, request.reason, "from", request.url, file=sys.stderr)
            return False
        return True

class ProgressBar:
    def __init__(self, count, prefix='', size=60, out=sys.stdout):
        self.count = count
        self.prefix = prefix + ' '
        self.size = size
        self.out = out
        self.start = time.time()
        self.tick(0)
    def tick(self, index):
        if self.count <= 0:
            return
        j = min(self.count, index + 1)
        x = int(self.size*j/self.count)
        current = time.time()
        if j <= 0:
            remaining = 0
        else:
            remaining = ((current - self.start) / j) * (self.count - j)
        mins, sec = divmod(remaining, 60)
        time_str = f"{int(mins):02}m:{int(sec):02}s"
        print(f"{self.prefix}[{u'#'*x}{('.'*(self.size-x))}] {index}/{self.count} ETA {time_str}", end='\r', file=self.out, flush=True)
        if j == self.count:
            print('')

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

if not os.path.isdir(k_data_dir):
    os.mkdir(k_data_dir)
os.chdir(k_data_dir)


# TODO refresh cookie only periodically, pickle it
# because it's slow
# or refresh it if it fails
cookie = GetCookie()
fetcher = Fetcher()

GetItems()

############
### TODO ###
############

# test the cookie
# find userID from cookie
# list inventory
# make repo
# git ignore
# test emacs-ripgrep works on project search
