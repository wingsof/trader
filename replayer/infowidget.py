from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QTableView
from PyQt5.QtCore import pyqtSlot, QAbstractTableModel, Qt
import speed_figure
from datetime import datetime


class SpreadModel(QAbstractTableModel):
    def __init__(self):
        super(QAbstractTableModel, self).__init__()
        self.trade_speed = [0] * 8
        self.spread_speed = [0] * 8

    def rowCount(self, parent):
        return 8

    def columnCount(self, parent):
        return 4

    def set_trade_speed(self, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30):
        self.trade_speed = [bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30]
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))


    def set_spread_speed(self, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30):
        self.spread_speed = [bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30]
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.TextAlignmentRole and index.column() % 2 == 0:
            return Qt.AlignCenter
        elif role == Qt.TextAlignmentRole and index.column() % 2 == 1:
            return Qt.AlignRight | Qt.AlignVCenter

        if role == Qt.DisplayRole and index.column() == 0:
            if index.row() % 2 == 0:
                return 'BID'
            else:
                return 'SPREAD'
        elif role == Qt.DisplayRole and index.column() == 1:
            if index.row() % 2 == 0:
                return self.trade_speed[int(index.row() / 2)]
            else:
                return self.spread_speed[index.row()]
        elif role == Qt.DisplayRole and index.column() == 3:
            if index.row() % 2 == 0:
                return self.trade_speed[int(index.row() / 2) + 1]
            else:
                return self.spread_speed[index.row() - 1]
        elif role == Qt.DisplayRole and index.column() == 2:
            if index.row() % 2 == 0:
                return 'ASK'
            else:
                return 'SPREAD'
        return None

class InfoWidget(QWidget):
    def __init__(self):
        super(InfoWidget, self).__init__()
        self.speed_label_widget = []
        self.defense_label_widget = []
        self.init_ui()

    def set_date(self, dt):
        self.spread_speed_figure.set_date(dt)

    def init_ui(self):
        self.layout = QGridLayout()
        self.spread_speed_table = QTableView()
        self.spread_speed_table.horizontalHeader().hide()
        self.spread_speed_table.verticalHeader().hide()

        self.spread_model = SpreadModel()
        self.spread_speed_table.setModel(self.spread_model)

        self.spread_speed_figure = speed_figure.SpeedFigure()

        self.layout.addWidget(self.spread_speed_table, 0, 0)
        self.layout.addWidget(self.spread_speed_figure, 1, 0)
        self.setLayout(self.layout)

    @pyqtSlot(datetime, float, float, float, float, float, float, float, float)
    def speedChanged(self, timestamp, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30):
        self.spread_model.set_trade_speed(bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30)
        self.spread_speed_figure.add_trade_speed(timestamp, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30)

    @pyqtSlot(datetime, float, float, float, float, float, float, float, float)
    def defenseChanged(self, timestamp, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30):
        self.spread_model.set_spread_speed(bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30)
        self.spread_speed_figure.add_spread_speed(timestamp, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30)

    @pyqtSlot(datetime, int, int, bool)
    def tradeChanged(self, timestamp, price, volume, is_long):
        pass
