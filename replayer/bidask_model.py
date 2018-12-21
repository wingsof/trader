from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import Qt
from pymongo import MongoClient
import time_converter
import unit, config
from datetime import timedelta
import pandas as pd
from PyQt5.QtCore import QDate, pyqtSlot, pyqtSignal
import before_market
import in_market


class BidAskModel(QAbstractTableModel):
    def __init__(self):
        super(BidAskModel, self).__init__()
        self.db = MongoClient('mongodb://127.0.0.1:27017').stock
        self.price_unit_list = []
        self.start_price = 0
        self.realtime_cursor = None
        self.buffered_data = None
        self.markets = {}
        self.current_market = config.UNKNOWN_MARKET

    def get_start_price(self):
        return self.start_price

    def get_close_price(self):
        return self.close_price

    def identify_market_type(self, d):
        market = d['20']
        if market == ord('1'):
            return config.BEFORE_MARKET
        elif market == ord('2'):
            return config.IN_MARKET
        elif market == ord('5'):
            return config.AFTER_MARKET
        return config.UNKNOWN_MARKET

    def fetch_a_sec_data(self, cursor):
        period_data = []
        timestamp = None
        market_type = None
        if self.buffered_data is not None:
            period_data.append(self.buffered_data)
            market_type = self.identify_market_type(self.buffered_data)
            timestamp = self.buffered_data['date']
            self.buffered_data = None
        
        while cursor.hasNext():
            d = cursor.next()
            data_market_type = self.identify_market_type(d)
            if timestamp is None:
                timestamp = d['date']
                market_type = data_market_type
                period_data.append(d)
            else:
                if d['date'] - timestamp < timedelta(seconds=1) and data_market_type == market_type:
                    period_data.append(d)
                else:
                    self.buffered_data = d
                    break
        return period_data, market_type

    @pyqtSlot()
    def next(self):
        if self.realtime_cursor is None:
            return

        sec_data, market_type = self.fetch_a_sec_data(self.realtime_cursor)

        if len(sec_data) == 0:
            return
        
        self.current_market = market_type

        if market_type is config.UNKNOWN_MARKET:
            pass
        else:
            self.markets[market_type].handle_data(sec_data)

    def set_bid_ask_price(self, start, high, low, close):
        current = high + unit.get_price_unit(high) * 5
        self.start_price = start
        self.close_price = close
        while current > low - unit.get_price_unit(low) * 5:
            self.price_unit_list.append(current)
            punit = unit.get_price_unit(current)
            current -= punit
        self.markets[config.BEFORE_MARKET] = before_market.BeforeMarket(self.price_unit_list)
        #self.markets[config.IN_MARKET] = in_market.InMarket(self.price_unit_list)

    def get_previous_date_close(self, code, dt):
        max_count = 10
        while max_count > 0:
            dt = dt - timedelta(days=1)
            cursor = self.db[code + '_D'].find({'0': time_converter.datetime_to_intdate(dt)})
            if cursor.count() > 0:
                return cursor.next()['5']
            max_count -= 1
        return 0

    def set_info(self, code, dt):
        cursor = self.db[code + '_D'].find({'0': time_converter.datetime_to_intdate(dt)})
        if cursor.count() == 0:
            print('cannot find day data', code, dt)
            return

        yesterday_close = self.get_previous_date_close(code, dt)

        if yesterday_close is 0:
            print('cannot find yesterday data', code, dt)
            return

        self.realtime_cursor = self.db[code].find({'date': {'$gt': dt, '$lt': dt + timedelta(days=1)}})
        if self.realtime_cursor.count() == 0:
            print('cannot find today tick datas', code, dt)
            return
        
        self.layoutAboutToBeChanged.emit()
        data = cursor.next()
        self.set_bid_ask_price(yesterday_close, data['3'], data['4'], data['5'])

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
        
        p = self.price_unit_list[index.row()]
        if role == Qt.DisplayRole and index.column() == config.PRICE_COL:
            return p
        elif role == Qt.DisplayRole and index.column() == config.PERCENTAGE_COL:
            percentage = (p - self.start_price) / self.start_price * 100.
            return '{0:0.2f}'.format(percentage)
        else:
            if self.current_market == config.BEFORE_MARKET:
                if index.column() == config.BID_QTY_COL or index.column() == config.BID_WEIGHT_COL or \
                    index.column() == config.ASK_QTY_COL or index.column() == config.ASK_WEIGHT_COL:
                    return self.markets[self.current_market].get_data(p, index.column(), role)    
                
        return None
