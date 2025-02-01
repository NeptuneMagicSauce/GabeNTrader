import os
import sys

class Common:
    def init():
        os.chdir(os.path.dirname(os.path.abspath(os.path.realpath(__file__)))) # chdir to main.py
        sys.path.append("../src")
