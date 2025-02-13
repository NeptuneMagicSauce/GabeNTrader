import re

from instances import *
from network import *
from utils import *
from remoteimages import *

class Steam:
    def initialize():
        # do not cache user_id
        # because it is used to validate the cookie
        Instances.user_id = Steam.get_user_id_from_chattoken()
        Instances.cookie_is_valid = Instances.user_id is not None
        print('UserId:', Instances.user_id)

        # debug: wait before sending status
        # threading.Thread(target=lambda: [time.sleep(1),
                                         # Steam.signals.login_validated.emit(Instances.cookie_is_valid)]).start()
        Steam.signals.login_validated.emit(Instances.cookie_is_valid)

    class Signals(QObject):
        login_validated = pyqtSignal(bool)
        user_id_found = pyqtSignal()

    signals = Signals()

    def get_user_id_from_chattoken():
        if c := Instances.fetcher.get_json('https://steamcommunity.com/chat/clientjstoken', throttle=False):
        # {
        #  "logged_in": false,
        #  "steamid": "",
        #  "accountid": 0,
        #  "account_name": "",
        #  "token": ""
        # }
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
        Instances.user_name = None
        user_icon_url = None

        if c := Instances.fetcher.get_text('https://steamcommunity.com/my/' + str(Instances.user_id), throttle=False):
            r_name = re.compile('<span class="actual_persona_name">(.*)</span>')
            r_pix = re.compile('< *img *.*(http.*_medium.[A-z]*)')
            for line in c.splitlines():
                if Instances.user_name and user_icon_url:
                    break

                if not Instances.user_name:
                    # use the first match, following matches are incorrect
                    if m := re.search(r_name, line):
                        n = m.groups()[0]
                        if OScompat.id == OScompat.ID.Windows:
                            # special chars fail on windows terminal
                            n = n.encode('ascii', 'ignore').decode("utf-8")
                        Instances.user_name = n
                        print('UserName:', Instances.user_name)

                if not user_icon_url:
                    # use the first match, following matches are incorrect
                    if m := re.search(r_pix, line):
                        n = m.groups()[0]
                        user_icon_url = n
                        # print('UserIcon:', n)

        if user_icon_url:
            if i := Images.get(user_icon_url, use_cache=True): # can change often
                Instances.user_icon = i

        Steam.signals.user_id_found.emit()

        # https://steamcommunity.com/profiles/$user_id/ajaxaliases
        # that's not the current name, that's the previous names
