from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import Qt
from pymongo import MongoClient
import time_converter
import unit, config


class BidAskModel(QAbstractTableModel):
    def __init__(self):
        super(BidAskModel, self).__init__()
        self.db = MongoClient('mongodb://127.0.0.1:27017').stock
        self.price_unit_list = []
        self.start_price = 0

    def get_start_price(self):
        return self.start_price

    def get_close_price(self):
        return self.close_price

    def set_bid_ask_price(self, start, high, low, close):
        current = high + unit.get_price_unit(high) * 5
        self.start_price = start
        self.close_price = close
        while current > low - unit.get_price_unit(low) * 5:
            self.price_unit_list.append(current)
            punit = unit.get_price_unit(current)
            current -= punit

    def set_info(self, code, dt):
        self.layoutAboutToBeChanged.emit()
        cursor = self.db[code + '_D'].find({'0': time_converter.datetime_to_intdate(dt)})
        if cursor.count() == 0:
            return
        data = cursor.next()
        self.set_bid_ask_price(data['2'], data['3'], data['4'], data['5'])
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self.price_unit_list)

    def columnCount(self, parent):
        return config.COLUMN_COUNT

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role != Qt.DisplayRole:
            return None
        
        p = self.price_unit_list[index.row()]
        if index.column() == config.PRICE_COL:
            return p
        elif index.column() == config.PERCENTAGE_COL:
            percentage = (p - self.start_price) / self.start_price * 100.
            return '{0:0.2f}'.format(percentage)
