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


class GUI:
    app = None

    def wait_for_load():
        assert(threading.current_thread() is not threading.main_thread())
        while GUI.app is None:
            time.sleep(0.01)

    class App(QApplication):
        start_webview = pyqtSignal()
        webview_finished = threading.Event()

        def __init__(self):
            super().__init__(sys.argv)
            self.start_webview.connect(self.start_webview_cb)

        def start_webview_cb(self):
            k_webview_storage = os.getcwd() + '/webview/' + OScompat.id_str
            webview.start(private_mode=False, storage_path=k_webview_storage)
            self.webview_finished.set()

    def run():
        print('GUI >>>', threading.current_thread())
        GUI.app = GUI.App()
        # instantiate widgets must be after ctor QApplication
        b = QLineEdit()
        b.show()
        return GUI.app.exec()
