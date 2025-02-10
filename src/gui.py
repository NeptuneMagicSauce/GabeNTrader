# https://www.riverbankcomputing.com/static/Docs/PyQt6/index.html
# https://doc.qt.io/qt-6/qtwidgets-module.html

import sys
import os
import time
import threading
import webview

from PyQt6.QtCore import QDateTime, Qt, QTimer, QMargins, QSize
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QScrollArea, QToolBar, QSizePolicy, QStyle, QToolButton )

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
        GUI.app = GUI.App()
        # instantiate widgets must be after ctor QApplication
        GUI.app.dialog = GUI.App.Dialog()
        return GUI.app.exec()

    class App(QApplication):
        start_webview = pyqtSignal('QString')
        webview_finished = threading.Event()
        tick_progress = pyqtSignal(int, int, 'QString')

        def __init__(self):
            super().__init__(sys.argv)
            self.setApplicationName('Trader')
            self.start_webview.connect(self.start_webview_cb)
            Instances.gui_out.event.connect(self.print_console_cb)
            self.tick_progress.connect(self.tick_progress_cb)

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
            if not lines.endswith('\n'):
                lines += '\n'
            logs = self.dialog.logs
            logs.setText(logs.text() + lines)
            logs.adjustSize() # must be called for correctness
            vscrollbar = self.dialog.logs_scroll.verticalScrollBar()
            vscrollbar.setValue(vscrollbar.maximum())

        def tick_progress_cb(self, index, count, label):
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

        class Dialog(QDialog):
            def __init__(self):
                super().__init__()
                self.setMinimumWidth(500)
                self.resize(500, 200)

                self.tool_bar = QToolBar()
                # self.tool_bar.setFixedHeight(20)
                self.tool_bar.setFloatable(False)
                self.tool_bar.setMovable(False)

                logs_button = QPushButton()#QToolButton() #'Logs')
                logs_button.setToolTip('Logs')
                icon = self.style().standardIcon(getattr(QStyle.StandardPixmap, 'SP_MessageBoxInformation'))
                logs_button.setIcon(icon)
                logs_button.setCheckable(True)
                logs_button.toggled.connect(lambda t: self.logs_scroll.setVisible(t))
                logs_spacer = QWidget()
                logs_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.tool_bar.addWidget(logs_spacer)
                self.tool_bar.addWidget(logs_button)

                root_layout = QVBoxLayout()
                self.r = root_layout
                root_layout.addWidget(self.tool_bar)

                main_layout = QVBoxLayout() # QGridLayout()
                root_layout.addLayout(main_layout)

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

                main_layout.addWidget(QLineEdit())#, 0, 0)
                main_layout.addWidget(QWidget())#)#, 1, 0) # spacer needed for tool_bar stays at fixed height
                main_layout.addWidget(QPushButton())#, 2, 0)
                main_layout.addWidget(self.logs_scroll)#, 3, 0)
                main_layout.addWidget(self.progress)#, 4, 0)

                self.progress.hide()
                self.logs_scroll.hide()

                self.setLayout(root_layout)
                self.show()
