# https://www.riverbankcomputing.com/static/Docs/PyQt6/index.html
# https://doc.qt.io/qt-6/qtwidgets-module.html

import sys
import os
import time
import threading
import webview

from PyQt6.QtCore import QDateTime, Qt, QTimer, QMargins, QSize
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QScrollArea, QToolBar, QSizePolicy, QStyle, QToolButton,
                             QMainWindow)

from instances import *
from utils import *
# import src.utils

class GUI:
    app = None

    def wait_for_load():
        assert(threading.current_thread() is not threading.main_thread())
        while GUI.app is None:
            time.sleep(0.01)

    def run():
        return GUI.App.run()

    class App(QApplication):

        # signals
        start_webview = pyqtSignal('QString')
        webview_finished = threading.Event()
        tick_progress = pyqtSignal(int, int, 'QString')

        # init
        def run():
            GUI.app = GUI.App()
            # instantiate widgets must be after ctor QApplication

            GUI.app.dialog = GUI.App.Central()
            w = QMainWindow()
            w.setWindowIcon(GUI.app.style().standardIcon(getattr(QStyle.StandardPixmap, 'SP_MessageBoxWarning')))
            w.setCentralWidget(GUI.app.dialog)
            w.addToolBar(GUI.App.ToolBar())

            w.show()
            return GUI.app.exec()

        # ctor
        def __init__(self):
            super().__init__(sys.argv)
            self.setApplicationName('Trader')
            self.start_webview.connect(self.start_webview_cb)
            Instances.gui_out.event.connect(self.print_console_cb)
            self.tick_progress.connect(self.tick_progress_cb)

        def start_webview_cb(self, storage_path):
            if Instances.deferred_quit:
                return
            # print('>>> start_webview_cb')
            # webview.start is slow and freezes the ui
            # but it must be done on the main thread
            # or on another process
            webview.start(private_mode=False, storage_path=storage_path)
            self.webview_finished.set()
            # print('<<< start_webview_cb')

        def print_console_cb(self, pid, thread, lines):
            if Instances.deferred_quit:
                return
            # builtins.print('>>>', pid, thread, lines, end='')
            if not lines.endswith('\n'):
                lines += '\n'
            logs = self.dialog.logs
            logs.setText(logs.text() + lines)
            logs.adjustSize() # must be called for correctness
            vscrollbar = self.dialog.logs_scroll.verticalScrollBar()
            vscrollbar.setValue(vscrollbar.maximum())

        def tick_progress_cb(self, index, count, label):
            if Instances.deferred_quit:
                return
            self.dialog.progress.tick(index, count, label)

        class ProgressBar(QWidget):

            def __init__(self):
                super().__init__()
                layout = QHBoxLayout()
                self.setLayout(layout)
                self.label = QLabel()
                layout.addWidget(self.label)
                self.bar = QProgressBar()
                self.bar.setMinimum(0)
                layout.addWidget(self.bar)
                self.ETA = QLabel()
                layout.addWidget(self.ETA)

            def tick(self, index, count, label):
                if index >= count:
                    self.hide()
                    self.label.setText('')
                    return
                self.show()
                index = clamp(index, 0, count)
                count = max(count, 1)
                if index == 0:
                    self.start = time.time()
                    self.ETA.setText('')
                else:
                    current = time.time()
                    elapsed = current - self.start
                    speed = index / elapsed
                    remaining = count - index
                    remaining_time = remaining / speed
                    mins, sec = divmod(remaining_time, 60)
                    time_str = f"{int(mins):02}m:{int(sec):02}s"
                    self.ETA.setText('ETA: ' + time_str)

                if len(label):
                    self.label.setText(label)
                self.bar.setMaximum(count)
                self.bar.setValue(index)

        class ToolBar(QToolBar):
            def __init__(self):
                super().__init__()
                self.setMovable(False)
                self.setFloatable(False)
                self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
                self.setFixedHeight(30)
                logs_spacer = QWidget()
                logs_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.addWidget(logs_spacer)
                self.logs_action = QAction() # must be a member otherwise it does not appear (destroyed?)
                logs_icon = GUI.app.style().standardIcon(getattr(QStyle.StandardPixmap, 'SP_MessageBoxInformation'))
                self.logs_action.setIcon(logs_icon)
                self.logs_action.setText('Logs')
                self.logs_action.setCheckable(True)
                self.logs_action.toggled.connect(lambda t: GUI.app.dialog.logs_scroll.setVisible(t))
                self.addAction(self.logs_action)

        class Central(QWidget):
            def __init__(self):
                super().__init__()
                self.setMinimumWidth(500)
                self.resize(500, 200)

                main_layout = QVBoxLayout() # QGridLayout()

                self.logs = QLabel()
                font = QFont("Monospace")
                font.setStyleHint(QFont.StyleHint.Monospace)#TypeWriter)
                font.setWeight(QFont.Weight.DemiBold)
                self.logs.setFont(font)
                self.logs_scroll = QScrollArea()
                # self.logs_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                # self.logs_scroll.resize(1, 50)
                self.logs_scroll.setWidget(self.logs)

                self.progress = GUI.App.ProgressBar()

                main_layout.addWidget(QLineEdit())
                main_layout.addWidget(QWidget()) # spacer exanding for QLineEdit to stay at the top
                main_layout.addWidget(QPushButton('Button'))
                main_layout.addWidget(self.logs_scroll)
                main_layout.addWidget(self.progress)

                self.progress.hide()
                self.logs_scroll.hide() # must be hidden to match logs_button state: not down

                self.setLayout(main_layout)
                self.show()
