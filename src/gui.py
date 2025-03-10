# https://www.riverbankcomputing.com/static/Docs/PyQt6/index.html
# https://doc.qt.io/qt-6/qtwidgets-module.html

import sys
import os
import time
import threading
import webview

from PyQt6.QtCore import QDateTime, Qt, QTimer, QMargins, QSize
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtCore import qInstallMessageHandler
from PyQt6.QtGui import QFont, QAction, QShortcut, QKeySequence
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QScrollArea, QToolBar, QSizePolicy, QStyle, QToolButton,
        QMainWindow, QStatusBar)

from instances import *
from utils import *
from emoji import *
from widgets import *

class GUI:
    ready = False
    quitted = False
    return_code = -1

    def wait_for_ready():
        assert(threading.current_thread() is not threading.main_thread())
        # GUI.ready is set after App() and App.initialize()
        while not GUI.ready:
            time.sleep(0.01)

    def run():
        return GUI.App.run()

    class App(QApplication):

        # signals
        start_webview = pyqtSignal('QString')
        webview_finished = threading.Event()
        tick_progress = pyqtSignal(int, int, 'QString')

        # init
        def initialize(self):

            def qt_message_handler(message_type, context, message):
                ignored = [
                    'Release of profile requested but WebEnginePage still not deleted',
                    # https://code.qt.io/cgit/qt/qtwebengine.git/tree/src/core/api/qwebenginepage.cpp?h=6.8#n582
                    # says it should not crash if we no longer access the page
                    'QGuiApplication::font(): no QGuiApplication instance and no application font set'
                    # comes from WebEngine
                    ]
                for i in ignored:
                    if message.startswith(i):
                        return
                builtins.print(message, file=sys.stderr)
            qInstallMessageHandler(qt_message_handler)

            # instantiate widgets must be after ctor QApplication
            # QMainWindow must be member of something otherwise it's destructed when leaving scope

            self.central = GUI.App.Central()
            self.main_window = QMainWindow()
            self.main_window.setWindowIcon(self.standard_icon('SP_MessageBoxWarning'))
            self.main_window.setCentralWidget(self.central)

            self.tool_bar = GUI.App.ToolBar(self)
            self.main_window.addToolBar(self.tool_bar)

            self.quit_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F12), self)
            self.quit_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut);
            self.quit_shortcut.activated.connect(self.quit)

            self.status_bar = GUI.App.StatusBar()
            self.main_window.setStatusBar(self.status_bar)
            self.status_bar.login.working.emit() # why not start in status working like Widgets.User ?

            # end widgets, they must be created before this line, because we're registering before_quit cb

            # before_quit cleanup: does not fix the spurious warning from WebEngine
            # when WebEngine (and QApplication) is deleted at end of main()
            # which is needed to not hang-up on exit waiting for WebEngine thread finish

            # def before_quit():
            #     # this is needed for the WebEngineProfile order destruction warning:
            #     # Release of profile requested but WebEnginePage still not deleted. Expect troubles
            #     self.central.login.page().deleteLater()
            #     # self.central.login_profile.deleteLater() # this hangs on quit
            # self.lastWindowClosed.connect(before_quit)

            self.main_window.show()
            GUI.ready = True

        def run(self):
            GUI.return_code = self.exec()
            GUI.quitted = True

            print('End')

        class Central(QWidget):
            def __init__(self):
                super().__init__()
                # self.setMinimumWidth(500)

                main_layout = QVBoxLayout() # QGridLayout()
                self.setLayout(main_layout)

                # logs
                self.logs = QLabel()
                font = QFont("Monospace")
                font.setStyleHint(QFont.StyleHint.Monospace)#TypeWriter)
                font.setWeight(QFont.Weight.DemiBold)
                self.logs.setFont(font)
                self.logs_scroll = QScrollArea()
                self.logs_scroll.setWidget(self.logs)
                self.logs_scroll.hide() # must be hidden to match logs_button state: not down

                # progress bar
                self.progress = GUI.App.ProgressBar()
                self.progress.hide()

                # login
                self.login = Widgets.Login()
                self.login.hide()

                # main widgets
                self.main_widgets = [
                    QLineEdit(),
                    QWidget(), # spacer exanding for QLineEdit to stay at the top
                    QPushButton('Button'),
                    self.logs_scroll,
                    self.progress,
                    ]

                # main
                main_layout.addWidget(self.login)
                for w in self.main_widgets:
                    main_layout.addWidget(w)

                self.show()

        # ctor
        def __init__(self):
            super().__init__(sys.argv)
            self.setApplicationName('Trader')
            self.start_webview.connect(self.start_webview_cb)
            self.tick_progress.connect(self.tick_progress_cb)

        def standard_icon(self, name):
            return self.style().standardIcon(getattr(QStyle.StandardPixmap, name))

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
            logs = self.central.logs
            logs.setText(logs.text() + lines)
            logs.adjustSize() # must be called for correctness
            vscrollbar = self.central.logs_scroll.verticalScrollBar()
            vscrollbar.setValue(vscrollbar.maximum())

        def tick_progress_cb(self, index, count, label):
            self.central.progress.tick(index, count, label)

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
                self.start = 0

            def tick(self, index, count, label):
                if index >= count and count:
                    self.hide()
                    self.label.setText('')
                    return
                self.show()
                index = clamp(index, 0, count)
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
            def __init__(self, app):
                super().__init__()
                self.setMovable(False)
                self.setFloatable(False)
                self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
                self.setFixedHeight(30)
                self.logs_action = QAction() # must be a member otherwise it does not appear (destroyed?)
                self.logs_action.setIcon(app.standard_icon('SP_MessageBoxInformation'))
                self.logs_action.setText('Logs')
                self.logs_action.setCheckable(True)
                self.logs_action.toggled.connect(lambda t: app.central.logs_scroll.setVisible(t))
                self.addAction(self.logs_action)
                logs_spacer = QWidget()
                logs_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.addWidget(logs_spacer)

                self.user_action = Widgets.User()
                self.addWidget(self.user_action)

        class StatusBar(QStatusBar):
            class Item(QWidget):

                set_text = pyqtSignal('QString')
                working = pyqtSignal()

                def __init__(self, name):
                    super().__init__()
                    layout = QHBoxLayout()
                    self.setLayout(layout)
                    layout.addWidget(QLabel(name + ':'))
                    self.status = QLabel('status')
                    layout.addWidget(self.status)
                    self.set_text.connect(self.set_text_cb)
                    self.working.connect(self.working_cb)
                    self.update = QTimer()
                    self.update.timeout.connect(self.update_cb)
                    self.spinner = Widgets.SpinnerAscii()
                    self.hide()

                def set_success(self, value):
                    self.update.stop()
                    self.status.setText(Emoji.check if value else Emoji.cross)
                    self.show()

                def set_text_cb(self, value):
                    self.update.stop()
                    self.status.setText(value)
                    self.show()
                def working_cb(self):
                    self.update.start(Widgets.SpinnerAscii.period)
                    self.update_cb() # fire it once so that we do not wait the first tick
                def update_cb(self):
                    self.status.setText(self.spinner.value())
                    self.show()



            def __init__(self):
                super().__init__()
                self.setSizeGripEnabled(False)
                self.login = GUI.App.StatusBar.Item('Login')
                self.addPermanentWidget(self.login)
                self.data = GUI.App.StatusBar.Item('Data')
                self.addPermanentWidget(self.data)
