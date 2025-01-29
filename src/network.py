#!/usr/bin/env python3

import requests
import json
import time
import sys

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
    def initialize(self, cookie):
        self.cookie = cookie
        # print(cookie)

    def __init__(self):
        super().__init__(period=2.5)
                         # 10.0)
                         #3.0)
                         # 2.5)
        self.cookie = ''

    def get(self, url):
        self.tick()
        ret = requests.get(url, cookies=self.cookie)

        with open('.latest.code', 'w') as c, open('.latest.json', 'w') as j, open('.latest.url', 'w') as u:
            print(ret.status_code, file=c)
            print(ret.url, file=u)
            if ret.status_code == requests.codes.ok:
                # print(ret.json(), file=j) # requests.json() fails to parse with jq
                print(json.dumps(json.loads(ret.content), indent=1), file=j)
            else:
                print('', file=j)
        return ret
    def check(request):
        if request.status_code != requests.codes.ok:
            print(request.reason, request.status_code, "from", request.url)
            return False
        return True

fetcher = Fetcher()
