from PyQt5.QtCore import Qt, QAbstractTableModel, QDate, pyqtSlot, pyqtSignal
from pymongo import MongoClient
import time_converter
import unit
from datetime import timedelta, datetime
import pandas as pd
import market_model, playable_market_model
import config


class BidAskModel(QAbstractTableModel):
    infoChanged = pyqtSignal(int, datetime)
    speedChanged = pyqtSignal(datetime, float, float, float, float, float, float, float, float)
    defenseChanged = pyqtSignal(datetime, float, float, float, float, float, float, float, float)
    tradeChanged = pyqtSignal(datetime, int, int, bool) # price, volume, buy / sell


    def __init__(self):
        super(BidAskModel, self).__init__()
        self.db_realtime = MongoClient(config.MONGO_SERVER).trade_alarm
        self.db = MongoClient(config.MONGO_SERVER).stock
        self.price_unit_list = []
        self.start_price = 0
        self.markets = {}
        self.current_market = config.BEFORE_MARKET

    def get_start_price(self):
        return self.start_price

    def get_close_price(self):
        return self.close_price

    def get_current_market(self):
        return self.current_market

    def get_price_len(self):
        return len(self.price_unit_list)

    def identify_market_type(self, d):
        market = d['20']
        if market == ord('1'):
            return config.BEFORE_MARKET
        elif market == ord('2'):
            return config.IN_MARKET
        elif market == ord('5'):
            return config.AFTER_MARKET
        return config.UNKNOWN_MARKET

    def identify_bid_type(self, d):
        if d['23'] != 0 or d['24'] != 0:
            return config.IN_MARKET
        else:
            if d['date'].hour >= 15:
                return config.AFTER_MARKET
            else:
                return config.BEFORE_MARKET

    # precondition: at least 1 data is exist in cursor
    def classify_data(self, realtime_cursor, ba_cursor):
        market_data = {config.IN_MARKET: [], config.AFTER_MARKET: [], config.BEFORE_MARKET: [], config.UNKNOWN_MARKET: []}
        r_data = realtime_cursor.next()
        ba_data = ba_cursor.next()
        while True:
            if ba_data is None and r_data is None:
                break
            elif ba_data is None:
                r_data['type'] = config.REALTIME_DATA
                market_data[self.identify_market_type(r_data)].append(r_data)
                try:
                    r_data = realtime_cursor.next()
                except StopIteration:
                    r_data = None
            elif r_data is None:
                ba_data['type'] = config.BIDASK_DATA
                market_data[self.identify_bid_type(ba_data)].append(ba_data)
                try:
                    ba_data = ba_cursor.next()
                except StopIteration:
                    ba_data = None                
            elif r_data['date'] < ba_data['date']:
                r_data['type'] = config.REALTIME_DATA
                market_data[self.identify_market_type(r_data)].append(r_data)
                try:
                    r_data = realtime_cursor.next()
                except StopIteration:
                    r_data = None
            else:
                ba_data['type'] = config.BIDASK_DATA
                market_data[self.identify_bid_type(ba_data)].append(ba_data)
                try:
                    ba_data = ba_cursor.next()
                except StopIteration:
                    ba_data = None
        return market_data

    def next(self):
        highlight = []
        if not self.markets[self.current_market].has_next():
            if self.current_market == config.BEFORE_MARKET:
                self.current_market = config.IN_MARKET
            elif self.current_market == config.IN_MARKET:
                if self.markets[config.AFTER_MARKET].has_next():
                    self.current_market == config.AFTER_MARKET
            elif self.current_market == config.AFTER_MARKET:
                self.current_market = config.IN_MARKET
        else:
            time, highlight = self.markets[self.current_market].next()
            self.infoChanged.emit(self.current_market, time)
            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(len(self.price_unit_list), config.COLUMN_COUNT))
        return highlight

    def prev(self):
        if self.markets[self.current_market].has_prev():
            time = self.markets[self.current_market].prev()
            self.infoChanged.emit(self.current_market, time)
            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(len(self.price_unit_list), config.COLUMN_COUNT))

    def set_bid_ask_price(self, start, high, low, close):
        current = high + unit.get_price_unit(high) * 10
        self.start_price = start
        self.close_price = close
        while current > low - unit.get_price_unit(low) * 10:
            self.price_unit_list.append(current)
            punit = unit.get_price_unit(current)
            current -= punit

    def get_previous_date_close(self, code, dt):
        max_count = 10
        while max_count > 0:
            dt = dt - timedelta(days=1)
            cursor = self.db[code + '_D'].find({'0': time_converter.datetime_to_intdate(dt)})
            if cursor.count() > 0:
                p = cursor.next()['5']
                print('CLOSE', dt, p)
                return p
            max_count -= 1
        return 0

    def set_info(self, code, dt):
        self.price_unit_list = []
        self.start_price = 0
        self.markets = {}
        self.current_market = config.BEFORE_MARKET
        cursor = self.db[code + '_D'].find({'0': time_converter.datetime_to_intdate(dt)})
        if cursor.count() == 0:
            print('cannot find day data', code, dt)
            return

        yesterday_close = self.get_previous_date_close(code, dt)

        if yesterday_close is 0:
            print('cannot find yesterday data', code, dt)
            return

        condition = {'date': {'$gt': dt, '$lt': dt + timedelta(days=1)}}
        realtime_cursor = self.db_realtime[code].find(condition)
        if realtime_cursor.count() == 0:
            print('cannot find today tick datas', code, dt)
            return
        
        bidask_cursor = self.db_realtime[code + '_BA'].find(condition)
        if bidask_cursor.count() == 0:
            print('cannot find bid ask spread', code, dt)
            return

        self.layoutAboutToBeChanged.emit()
        data = cursor.next()
        self.set_bid_ask_price(yesterday_close, data['3'], data['4'], data['5'])
        market_data = self.classify_data(realtime_cursor, bidask_cursor)
        self.markets[config.BEFORE_MARKET] = market_model.MarketModel(self.price_unit_list, market_data[config.BEFORE_MARKET])
        self.markets[config.IN_MARKET] = playable_market_model.PlayableMarketModel(self.price_unit_list, market_data[config.IN_MARKET])
        self.markets[config.IN_MARKET].speedChanged.connect(self.speedChanged)
        self.markets[config.IN_MARKET].defenseChanged.connect(self.defenseChanged)
        self.markets[config.IN_MARKET].tradeChanged.connect(self.tradeChanged)
        self.markets[config.AFTER_MARKET] = market_model.MarketModel(self.price_unit_list, market_data[config.AFTER_MARKET])

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
            if (index.column() >= 0 and index.column() <= 2) or (index.column() >= 5 and index.column() <= 7):
                return self.markets[self.current_market].get_data(p, index.column(), role)
                
        return None
