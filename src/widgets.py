import unicodedata
from PyQt6.QtCore import QTimer, Qt, QUrl, QLoggingCategory, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtNetwork import QNetworkCookie
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

from utils import *
from instances import *
from emoji import *

class Widgets:

    class SpinnerAscii:
        period = 50 # milliseconds
        # from braille unicode
        # https://www.unicode.org/charts/nameslist/n_2800.html#2800
        # https://www.fileformat.info/info/unicode/block/braille_patterns/images.htm
        def build_values():
            a = list([
                0x2801,
                0x2809,
                0x2819,
                0x281b,
                0x281f,
                0x283f,
                0x28bf,
                0x28ff,

                0x28fe,
                0x28f6,
                0x28e6,
                0x28e4,
                0x28e0,
                0x28c0,
                0x2840,
                # 0x2800, # blank
            ])
            # copy reversed for looping
            a_reversed = list(reversed(a))
            # remove duplicated boundaries so that they don't repeat
            a_reversed.pop(0)
            a_reversed.pop(len(a_reversed)-1)
            a.extend(a_reversed)
            return list(map(chr, a))
        values = build_values()
        length = len(values)

        def __init__(self):
            self.index = 0
        def value(self):
            ret = Widgets.SpinnerAscii.values[self.index]
            self.index += 1
            if  self.index == Widgets.SpinnerAscii.length:
                self.index = 0
            return ret

    class User(QWidget):
        def __init__(self):
            super().__init__()
            self.update = QTimer()
            self.update.timeout.connect(self.update_cb)
            self.spinner = Widgets.SpinnerAscii()
            layout = QHBoxLayout()
            self.setLayout(layout)
            self.image = QLabel()
            self.name = QLabel()
            layout.addWidget(self.image)
            layout.addWidget(self.name)
            self.update.start(Widgets.SpinnerAscii.period)

            margins = layout.contentsMargins()
            margins.setTop(0)
            margins.setBottom(0)
            layout.setContentsMargins(margins)

        def update_cb(self):
            self.name.setText(self.spinner.value())

        def found(self):
            if n := Instances.user_name:
                self.name.setText(n)
            else:
                self.name.setText('?')

            try:
                if i := Instances.user_icon:
                    pix = QPixmap()
                    if pix.loadFromData(i):
                        self.image.setPixmap(pix.scaled(
                            self.image.height(), self.image.height(),
                            Qt.AspectRatioMode.KeepAspectRatio))
                    else:
                        raise
                else:
                    raise
            except:
                self.image.setText(Emoji.question_mark)
            self.update.stop()

    class Login(QWebEngineView):

        found = pyqtSignal()

        def __init__(self):
            self.k_cookie_key = "steamLoginSecure"

            k_storage_name = 'webviewqt'
            # profile must be a member otherwise it's deleted at end of constructor
            self.profile = QWebEngineProfile(k_storage_name)
            k_webview_storage = os.getcwd() + '/' + k_storage_name
            self.profile.setCachePath(k_webview_storage + '/cache')
            self.profile.setPersistentStoragePath(k_webview_storage + '/storage')
            # profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies) # not needed

            super().__init__(self.profile)

            store = self.profile.cookieStore()
            # store.loadAllCookies() # does not load cookies before self.load() !
            store.cookieAdded.connect(self.cookie_added)

            self.k_url = QUrl('https://steamcommunity.com/login/home')
            self.load(self.k_url)

            # do not allow to change the url
            self.urlChanged.connect(lambda: self.setUrl(self.k_url))

            # inhibit java script warnings in the console
            QLoggingCategory.setFilterRules('js=false')

            # inhibit context menu
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

            # this is required otherwise on deferred show we must expand the window
            self.setMinimumSize(500, 500)

            # TODO
            # - find a better fix than minimum size, maybe refresh layout, repaint,
            #   central.resize() does not seem to work either
            #   maybe size policy expanding
            #   maybe zoom is too big because of dpi bug
            # - why is thread/process stuck on exit now? randomly
            #   because of deleteLater?
            # - have good size: i want to see the QR code
            # - connect login.found to steam.on_cookie_found (or active wait ?!)
            # - refresh if invalid
            # - find the cookie from the previous session: where's the api for that ?!
            #   or do we need it? is is pickled!
            # - obsolete most of cookie.py in src/oldies (or src/obsolete)

        def cookie_added(self, cookie):

            print('Debug remove this')
            QTimer.singleShot(1000, self.found.emit)

            for sub_cookie in QNetworkCookie.parseCookies(cookie.toRawForm()):
                def qbytes_to_str(b):
                    return bytes(b).decode('utf-8')
                name = qbytes_to_str(sub_cookie.name())
                if name == self.k_cookie_key:
                    value = qbytes_to_str(sub_cookie.value())
                    Instances.cookie = { self.k_cookie_key, value }
                    self.found.emit()
                    self.hide()
                    # print('Cookie', name, value)
