from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, pyqtSlot, pyqtSignal
import bidask_model
import menuwidget
import actionwidget
import bidask_view
import infowidget

from datetime import datetime

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.init_ui()
        self.menu.info_changed.connect(self.set_info)

    @pyqtSlot(str, datetime)
    def set_info(self, code, dt):
        self.table.set_info(code, dt)

    def init_ui(self):
        self.layout = QGridLayout()
        self.menu = menuwidget.MenuWidget()
        self.table = bidask_view.BidAskView()
        
        self.info = infowidget.InfoWidget()
        self.action = actionwidget.ActionWidget()
        self.action.go_next.connect(self.table.next)
        self.action.go_prev.connect(self.table.prev)
        self.action.play.connect(self.table.play)
        self.action.stop.connect(self.table.stop)

        self.table.infoChanged.connect(self.action.infoChanged)
        self.table.speedChanged.connect(self.info.speedChanged)
        self.table.defenseChanged.connect(self.info.defenseChanged)

        self.layout.addWidget(self.menu, 0, 0)
        self.layout.addWidget(self.table, 1, 0)
        self.layout.addWidget(self.info, 1, 1)
        self.layout.addWidget(self.action, 2, 0)
        self.setLayout(self.layout)