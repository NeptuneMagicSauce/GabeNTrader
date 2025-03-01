import requests
import json
import time
import sys
from enum import Enum

from instances import *

class RateLimiter:
    def __init__(self, period):
        self.k_period = period
        self.last_time = float(-1)
    def tick(self, throttle=True):
        if throttle:
            if self.last_time > 0:
                elapsed = time.time() - self.last_time
                to_wait = max(0.0, self.k_period - elapsed)
                time.sleep(to_wait)
        self.last_time = time.time()

class Fetcher(RateLimiter):
    class Expect(Enum):
        JSON = 1
        Text = 2
        Binary = 3

    def __init__(self, cookie):
        super().__init__(period=2.5)
                         # 10.0)
                         #3.0)
                         # 2.5)
        self.cookie = cookie

    def get_json(self, url, throttle=True):
        return Fetcher.convert(self.get(url, throttle), Fetcher.Expect.JSON)

    def get_text(self, url, throttle=True):
        return Fetcher.convert(self.get(url, throttle), Fetcher.Expect.Text)

    def get_binary(self, url, throttle=True):
        return Fetcher.convert(self.get(url, throttle), Fetcher.Expect.Binary)

    def get(self, url, throttle=True):
        self.tick(throttle)
        ret = requests.get(url, cookies=self.cookie)
        try:
            print(ret.status_code, file=open(".latest.code", "w"))
            print(url, file=open(".latest.url", "w"))
            print(ret.text, file=open('.latest.text', 'w'))
            pickle.dump(ret.content, file=open('.latest.bin.pkl', 'wb'))
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

class Network:
    def initialize():
        Instances.fetcher = Fetcher(Instances.cookie)
