import os
import sys

class Common:
    def init():
        # /utils helpers will find library files in /src like this:
        sys.path.append(os.path.dirname(os.path.abspath(os.path.realpath(__file__))) + '/../src')
