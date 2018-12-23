from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPalette
from datetime import datetime
import bidask_model
import config

class BidAskDelegate(QStyledItemDelegate):
    def __init__(self):
        super(BidAskDelegate, self).__init__()

    def paint(self, painter, option, index):
        if index.column() == config.PERCENTAGE_COL:
            model = index.model()
            start_price = model.get_start_price()
            close_price = model.get_close_price()
            price = model.createIndex(index.row(), config.PRICE_COL).data()
            if price == close_price:
                painter.fillRect(option.rect, Qt.yellow)
            elif price < start_price:
                option.palette.setColor(QPalette.Text, Qt.white)
                painter.fillRect(option.rect, Qt.blue)
            elif price > start_price:
                option.palette.setColor(QPalette.Text, Qt.white)
                painter.fillRect(option.rect, Qt.red)

        QStyledItemDelegate.paint(self, painter, option, index)


class BidAskTable(QTableView):
    def __init__(self):
        super(BidAskTable, self).__init__()
        self.delegate = BidAskDelegate()
        self.setItemDelegate(self.delegate)


class BidAskView(QWidget):
    infoChanged = pyqtSignal(int, datetime)

    def __init__(self):
        super(BidAskView, self).__init__()
        self.model = bidask_model.BidAskModel()
        self.model.infoChanged.connect(self.infoChanged)
        self.init_ui()

    @pyqtSlot()
    def next(self):
        self.model.next()

    def set_info(self, code, dt):
        self.model.set_info(code, dt)

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.table = BidAskTable()
        self.table.setModel(self.model)
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)