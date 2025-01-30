import re

from network import *
from utils import *

k_userid_path = "userid"

def GetUserId():
    try:
        return pickle_load(k_userid_path)
    except:
        pass

    c = fetcher.get_text("https://steamcommunity.com/my/profile")
    if c is None:
        return None

    regexp = re.compile('g_steamID\\s=\\s"(.*)"')

    for l in c.splitlines():
        match = regexp.search(l)
        if match:
            groups = match.groups()
            if len(groups):
                id = groups[0]
                try:
                    ret = int(id)
                except:
                    print('failed to convert user id to string', l)
                    return None
                try:
                    pickle_save(ret, k_userid_path, compress=False)
                except:
                    pass
                return ret
            else:
                print('user id: regexp matched but no groups')
    return None

# TODO run in parallel as soon as possible
# TODO invalidate cache: if cookie changed or if change account
