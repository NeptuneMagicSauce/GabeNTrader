import unicodedata

class Widgets:
    class SpinnerAscii:
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
