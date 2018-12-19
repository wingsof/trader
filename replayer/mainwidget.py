from PyQt5.QtWidgets import *
import bidask_model
import menuwidget
import actionwidget
import bidaskview
import infowidget

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.layout = QGridLayout()
        self.menu = menuwidget.MenuWidget()
        self.table = bidaskview.BidAskView()
        self.info = infowidget.InfoWidget()
        self.action = actionwidget.ActionWidget()

        self.layout.addWidget(self.menu, 0, 0)
        self.layout.addWidget(self.table, 1, 0)
        self.layout.addWidget(self.info, 1, 1)
        self.layout.addWidget(self.action, 2, 0)
        self.setLayout(self.layout)
        """
        self.table_view = QTableView()
        self.table_model = bidask_model.BidAskModel()
        self.table_view
        """