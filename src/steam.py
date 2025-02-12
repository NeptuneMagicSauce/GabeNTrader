import re

from instances import *
from network import *
from utils import *

class Steam:
    def initialize():
        # do not cache user_id
        # because it is used to validate the cookie
        Instances.user_id = Steam.get_user_id_from_chattoken()
        Instances.cookie_is_valid = Instances.user_id is not None
        print('UserId:', Instances.user_id)
        Steam.signals.login_validated.emit(Instances.cookie_is_valid)

    class Signals(QObject):
        login_validated = pyqtSignal(bool)
    signals = Signals()

    def get_user_id_from_chattoken():
        c = Instances.fetcher.get_json('https://steamcommunity.com/chat/clientjstoken', throttle=False)
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
        return None

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
        if c := Instances.fetcher.get_text('https://steamcommunity.com/my/' + str(Instances.user_id), throttle=False):
            r = re.compile('<span class="actual_persona_name">(.*)</span>')
            for line in c.splitlines():
                if m := re.search(r, line):
                    n = m.groups()[0]
                    if OScompat.id == OScompat.ID.Windows:
                        # special chars fail on windows terminal
                        n = n.encode('ascii', 'ignore').decode("utf-8")
                    Instances.user_name = n
                    print('UserName:', Instances.user_name)
                    return
        # https://steamcommunity.com/profiles/$user_id/ajaxaliases
        # that's not the current name, that's the previous names
