#!/usr/bin/env python3

import requests
import json
import time
import sys
from enum import Enum

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
    class Expect(Enum):
        JSON = 1
        Text = 2
        Binary = 3

    def initialize(self, cookie):
        self.cookie = cookie
        # print(cookie)

    def __init__(self):
        super().__init__(period=2.5)
                         # 10.0)
                         #3.0)
                         # 2.5)
        self.cookie = ''

    def get_json(self, url):
        response = self.get(url)
        return Fetcher.convert(response, Fetcher.Expect.JSON)

    def get(self, url):
        self.tick()
        ret = requests.get(url, cookies=self.cookie)
        try:
            print(ret.status_code, file=open(".latest.code", "w"))
            print(ret.url, file=open(".latest.url", "w"))
        except:
            pass
        return ret

    def convert(response, expect):
        if not Fetcher.check(response):
            return None
        match expect:
            case Fetcher.Expect.JSON:
                try:
                    # response.json() # this fails to parse with jq
                    ret = json.loads(response.content)
                    try:
                        print(json.dumps(ret, indent=1), file=open(".latest.json", "w"))
                    except:
                        pass
                    return ret
                except:
                    print("failed to parse JSON for", response.url)
                    return None
            case Fetcher.Expect.Text:
                return response.text
            case Fetcher.Expect.Binary:
                return response.content
        return None

    def check(response):
        if response.status_code != requests.codes.ok:
            print(response.reason, response.status_code, "from", response.url)
            return False
        return True

fetcher = Fetcher()
