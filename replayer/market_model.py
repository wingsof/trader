import config
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta


class MarketModel:
    def __init__(self, price_list, data_list, td=60):
        self.price_list = price_list
        self.data_list = data_list
        self.bid_trade_qty = {}
        self.ask_trade_qty = {}
        self.bid_spread_qty = {}
        self.ask_spread_qty = {}
        self.bid_weight = {}
        self.ask_weight = {}
        self.all_qty = 0
        self.timedelta = td

    def has_next(self):
        if len(self.data_list) > 0:
            return True
        return False
    
    def prev(self):
        pass

    def next(self):
        current_frame = [self.data_list.pop(0)]
        data = current_frame[0]
        while len(self.data_list) > 0:
            if self.data_list[0]['date'] - data['date'] < timedelta(seconds=self.timedelta):
                current_frame.append(self.data_list.pop(0))
            else:
                break
        self.process_data(current_frame)
        return current_frame[-1]['date'], []

    def add_data_to_dict(self, price, qty, d):
        if price in d:
            d[price].append(qty)
        else:
            d[price] = [qty]

    def plus_data_to_dict(self, price, qty, d):
        if price in d:
            d[price] += qty
        else:
            d[price] = qty

    def process_data(self, current_frame):
        for cf in current_frame:
            if cf['type'] == config.REALTIME_DATA:
                self.bid_trade_qty = {}
                self.ask_trade_qty = {}
                qty = cf['17']
                self.all_qty += qty
                print(cf['13'], qty, cf['18'], self.all_qty)
                if cf['26'] == ord('1'): #bid
                    self.add_data_to_dict(cf['13'], qty, self.bid_trade_qty)
                    self.plus_data_to_dict(cf['13'], qty, self.bid_weight)
                else:
                    self.add_data_to_dict(cf['13'], qty, self.ask_trade_qty)
                    self.plus_data_to_dict(cf['13'], qty, self.ask_weight)
            else:
                self.bid_spread_qty = {}
                self.ask_spread_qty = {}
                for p in config.BID_PAIR:
                    price = cf[p[0]]
                    qty = cf[p[1]]
                    self.bid_spread_qty[price] = qty
                for p in config.ASK_PAIR:
                    price = cf[p[0]]
                    qty = cf[p[1]]
                    self.ask_spread_qty[price] = qty
        #print(self.bid_trade_qty, self.bid_spread_qty, self.ask_spread_qty, self.ask_trade_qty)

    def get_data(self, price, col, role):
        if role == Qt.DisplayRole:
            if col == config.BID_TRADE_QTY_COL and price in self.bid_trade_qty:
                return sum(self.bid_trade_qty[price])
            elif col == config.BID_WEIGHT_COL and price in self.bid_weight:
                w = self.bid_weight[price] / self.all_qty * 100.
                if w > 0.:
                    return '{0:0.1f}'.format(w)
            elif col == config.ASK_TRADE_QTY_COL and price in self.ask_trade_qty:
                return sum(self.ask_trade_qty[price])
            elif col == config.ASK_WEIGHT_COL and price in self.ask_weight:
                w = self.ask_weight[price] / self.all_qty * 100.
                if w > 0.:
                    return '{0:0.1f}'.format(w)
            elif col == config.BID_SPREAD_QTY_COL and price in self.bid_spread_qty:
                return self.bid_spread_qty[price]
            elif col == config.ASK_SPREAD_QTY_COL and price in self.ask_spread_qty:
                return self.ask_spread_qty[price]
            
            return None
            
        return None