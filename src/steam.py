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
            Instances.user_id = Steam.get_user_id_from_chattoken()
            if Instances.user_id is not None:
                pickle_save(Instances.user_id, k_userid_path)

        Instances.cookie_is_valid = Instances.user_id is not None
        print('UserId:', Instances.user_id)


    def get_user_id_from_chattoken():
        c = Instances.fetcher.get_json('https://steamcommunity.com/chat/clientjstoken')
        # {
        #  "logged_in": false,
        #  "steamid": "",
        #  "accountid": 0,
        #  "account_name": "",
        #  "token": ""
        # }
        if c is None:
            return None
        try:
            return int(c['steamid'])
        except:
            pass

    # deprecated by get_user_id_from_chattoken()
    def get_user_id_from_profile():
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

    def get_user_name():
        if c := Instances.fetcher.get_json('https://steamcommunity.com/profiles/' + str(Instances.user_id) + '/ajaxaliases'):
            if len(c) and 'newname' in c[0]:
                n = c[0]['newname']
                if OScompat.id == OScompat.ID.Windows:
                    # special chars fail on windows terminal
                    n = n.encode('ascii', 'ignore').decode("utf-8")
                Instances.user_name = n
                print('UserName:', Instances.user_name)


# TODO run in parallel as soon as possible
# TODO invalidate cached user_id if account changed
