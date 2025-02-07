# https://www.riverbankcomputing.com/static/Docs/PyQt6/index.html
# https://doc.qt.io/qt-6/qtwidgets-module.html

import sys
import os
import time
import threading
import webview

from PyQt6.QtCore import QDateTime, Qt, QTimer
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

from instances import *
from utils import *
# import src.utils

class GUI:
    app = None

    def wait_for_load():
        assert(threading.current_thread() is not threading.main_thread())
        while GUI.app is None:
            time.sleep(0.01)

    class App(QApplication):
        start_webview = pyqtSignal('QString')
        webview_finished = threading.Event()

        def __init__(self):
            super().__init__(sys.argv)
            self.start_webview.connect(self.start_webview_cb)
            Instances.gui_out.event.connect(self.print_console_cb)

        def start_webview_cb(self, storage_path):
            # print('>>> start_webview_cb')
            # webview.start is slow and freezes the ui
            # but it must be done on the main thread
            # or on another process
            webview.start(private_mode=False, storage_path=storage_path)
            self.webview_finished.set()
            # print('<<< start_webview_cb')

        def print_console_cb(self, pid, thread, lines):
            # builtins.print('>>>', pid, thread, lines, end='')
            pass

    def run():
        GUI.app = GUI.App()
        # instantiate widgets must be after ctor QApplication
        b = QLineEdit()
        b.show()
        return GUI.app.exec()
