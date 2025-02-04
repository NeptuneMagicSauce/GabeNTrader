import sys
import time
import threading

from PyQt6.QtCore import QDateTime, Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

from instances import *
from utils import *


class GUI:
    return_code = None
    def initialize():
        print('GUI >>>', threading.current_thread())

        app = QApplication(sys.argv)
        b = QLineEdit()
        b.show()
        return_code = app.exec()
