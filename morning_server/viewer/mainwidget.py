from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, pyqtSlot, pyqtSignal

from datetime import datetime
import menuwidget
import figure
import data_handler

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.handler = data_handler.DataHandler()

        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()
        self.menu = menuwidget.MenuWidget()
        self.figure = self.handler.get_figure()

        self.menu.info_changed.connect(self.handler.info_changed)
        self.menu.check_next.connect(self.handler.check_next)
        self.menu.next_code.connect(self.handler.next_code)
        self.layout.addWidget(self.menu, 0, 0)
        self.layout.addWidget(self.figure, 1, 0)
        self.setLayout(self.layout)
