from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, pyqtSlot, pyqtSignal

from datetime import datetime

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)
