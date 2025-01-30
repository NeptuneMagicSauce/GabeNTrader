import re

from network import *

def GetUserId():
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
                    return int(id)
                except:
                    print('failed to convert user id to string', l)
            else:
                print('user id: regexp matched but no groups')
    return None


# TODO run in parallel as soon as possible
# TODO cache result of UserID (per cookie?)
