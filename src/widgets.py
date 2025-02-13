import unicodedata
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
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
