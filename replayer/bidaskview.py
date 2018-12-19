from PyQt5.QtWidgets import *
import bidask_model


class BidAskView(QWidget):
    def __init__(self):
        super(BidAskView, self).__init__()
        self.model = bidask_model.BidAskModel()
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)