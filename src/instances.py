from PyQt6.QtCore import QObject, pyqtSignal

# this instance can not be in gui.py because it would be cyclic imports with utils.py
class GUIOut(QObject):
    event = pyqtSignal(int, 'QString', 'QString')

class Instances:
    user_id = None
    user_name = ''
    cookie = {}
    cookie_is_valid = False
    items = []
    names = []
    fetcher = None
    is_main_process = False
    gui_out = GUIOut()
    deferred_quit = False
