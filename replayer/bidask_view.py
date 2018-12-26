from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPalette
from datetime import datetime
import bidask_model
import config
from PyQt5.QtCore import QTimer


class BidAskDelegate(QStyledItemDelegate):
    def __init__(self):
        super(BidAskDelegate, self).__init__()
        self.highlight = []

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
        else:
            model = index.model()
            for h in self.highlight:
                price = model.createIndex(index.row(), config.PRICE_COL).data()
                if h[2] == price:
                    if h[0] == config.REALTIME_DATA:
                        if  index.column() == config.BID_TRADE_QTY_COL and h[1]:
                            option.palette.setColor(QPalette.Text, Qt.white)
                            painter.fillRect(option.rect, Qt.red)    
                        elif index.column() == config.ASK_TRADE_QTY_COL and not h[1]:
                            option.palette.setColor(QPalette.Text, Qt.white)
                            painter.fillRect(option.rect, Qt.red)
                    elif h[0] == config.BIDASK_DATA:
                        if index.column() == config.BID_SPREAD_QTY_COL and h[1]:
                            option.palette.setColor(QPalette.Text, Qt.white)
                            painter.fillRect(option.rect, Qt.red)
                        elif index.column() == config.ASK_SPREAD_QTY_COL and not h[1]:
                            option.palette.setColor(QPalette.Text, Qt.white)
                            painter.fillRect(option.rect, Qt.red)

        QStyledItemDelegate.paint(self, painter, option, index)

    def set_highlight(self, highlight):
        self.highlight = highlight


class BidAskTable(QTableView):
    def __init__(self):
        super(BidAskTable, self).__init__()
        self.delegate = BidAskDelegate()
        self.setItemDelegate(self.delegate)

    def set_highlight(self, highlight):
        self.delegate.set_highlight(highlight)

class BidAskView(QWidget):
    infoChanged = pyqtSignal(int, datetime)
    speedChanged = pyqtSignal(datetime, float, float, float, float, float, float, float, float)
    defenseChanged = pyqtSignal(datetime, float, float, float, float, float, float, float, float)

    def __init__(self):
        super(BidAskView, self).__init__()
        self.model = bidask_model.BidAskModel()
        self.model.infoChanged.connect(self.infoChanged)
        self.model.speedChanged.connect(self.speedChanged)
        self.model.defenseChanged.connect(self.defenseChanged)

        self.timer = QTimer()
        self.timer.timeout.connect(self.run_timer)
        self.init_ui()

    @pyqtSlot()
    def next(self):
        highlight = self.model.next()
        if len(highlight) > 0:
            self.table.set_highlight(highlight)
            self.model.dataChanged.emit(self.model.createIndex(0, 0), self.model.createIndex(self.model.get_price_len(), config.COLUMN_COUNT))
            if self.timer.isActive():
                self.timer.stop()
        else:
            self.table.set_highlight([])

    @pyqtSlot()
    def prev(self):
        self.model.prev()
        self.table.set_highlight([])

    @pyqtSlot()
    def run_timer(self):
        if self.model.get_current_market() == config.IN_MARKET:
            self.next()
        else:
            self.time.stop()

    @pyqtSlot()
    def play(self):
        if not self.timer.isActive() and self.model.get_current_market() == config.IN_MARKET:
            self.timer.start(10)
    
    @pyqtSlot()
    def stop(self):
        if self.timer.isActive():
            self.timer.stop()

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