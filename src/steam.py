import re

from instances import *
from network import *
from utils import *

class Steam:
    def initialize():
        k_userid_path = "userid"
        try:
            Instances.user_id = pickle_load(k_userid_path)
        except:
            Instances.user_id = Steam.get_user_id()
            pickle_save(Instances.user_id, k_userid_path)

        Instances.cookie_is_valid = Instances.user_id is not None
        print('UserId:', Instances.user_id)

    def get_user_id():
        c = Instances.fetcher.get_text("https://steamcommunity.com/my/profile")
        if c is None:
            return None

        regexp_authenticated = re.compile('g_steamID\\s=\\s"([0-9]*)"')
        regexp_anonymous = re.compile('g_steamID\\s=\\s([A-z]*);')

        for l in c.splitlines():
            if match := regexp_authenticated.search(l):
                try:
                    ret = int(match.groups()[0])
                except:
                    print('failed to convert user id to string', l, match.groups()[0], sep='\n')
                    break
                return ret

            if match := regexp_anonymous.search(l):
                # print('match the non-authenticated user id:', match.groups()[0])
                break

        return None

# TODO run in parallel as soon as possible
# TODO invalidate cached user_id if account changed
