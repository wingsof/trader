import config
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QObject, pyqtSignal
from datetime import datetime, timedelta
import copy


class PlayableMarketModel(QObject):
    statusChanged = pyqtSignal(int)
    speedChanged = pyqtSignal(float, float, float, float, float, float, float, float) # 1, 10, 20, 30 min bid, ask pair

    def __init__(self, price_list, data_list):
        super(PlayableMarketModel, self).__init__()
        self.price_list = price_list
        self.data_list = data_list
        self.frame = {
            'index': 0,
            'time': data_list[0]['date'],
            'bid_trade_qty': {},
            'ask_trade_qty': {},
            'bid_spread_qty': {},
            'ask_spread_qty': {},
            'bid_weight': {},
            'ask_weight': {},
            'all_qty': 0,
        }
        self.history = []
        
    def has_next(self):
        if len(self.data_list) > self.frame['index']:
            return True
        return False

    def has_prev(self):
        if len(self.history) > 0:
            return True
        return False
        
    def prev(self):
        self.frame = self.history.pop()
        self.report_qty_speed()
        return self.frame['time']

    def capture_current(self):
        capture = copy.deepcopy(self.frame)
        capture['index'] = self.frame['index']
        self.history.append(capture)
    
    def next(self):
        self.capture_current()
        current_frame = [self.data_list[self.frame['index']]]
        self.frame['index'] += 1
        highlight = self.process_data(current_frame)

        self.frame['time'] = current_frame[0]['date']
        self.report_qty_speed()
        return current_frame[0]['date'], highlight

    def report_qty_speed(self):
        index = self.frame['index']
        one_min = self.get_qty_speed(1, index)
        ten_min = self.get_qty_speed(10, index)
        twenty_min = self.get_qty_speed(20, index)
        thirty_min = self.get_qty_speed(30, index)
        self.speedChanged.emit(one_min[0], one_min[1], ten_min[0], ten_min[1], twenty_min[0], twenty_min[1], 
                            thirty_min[0], thirty_min[1])

    def get_qty_speed(self, minute, index):
        start_time = self.data_list[index]['date']
        bid_qty = 0
        ask_qty = 0
        for i in range(index, -1, -1):
            if self.data_list[i]['type'] == config.REALTIME_DATA:
                if start_time - self.data_list[i]['date'] <= timedelta(minutes=minute):
                    if self.data_list[i]['26'] == ord('1'):
                        bid_qty += self.data_list[i]['17']
                    else:
                        ask_qty += self.data_list[i]['17']
                else:
                    break
        return bid_qty / minute, ask_qty / minute

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

    def compare_spread(self, before_spread, current_qty, price):
        if price not in before_spread:
            if current_qty * price >= config.HIGHLIGHT_PRICE:
                return price
        else:
            if abs((before_spread[price] - current_qty) * price) >= config.HIGHLIGHT_PRICE:
                return price
        return 0

    def process_data(self, current_frame):
        highlight_price = []
        for cf in current_frame:
            if cf['type'] == config.REALTIME_DATA:
                self.frame['bid_trade_qty'] = {}
                self.frame['ask_trade_qty'] = {}
                qty = cf['17']
                self.frame['all_qty'] += qty
                if cf['26'] == ord('1'): #bid
                    self.add_data_to_dict(cf['13'], qty, self.frame['bid_trade_qty'])
                    self.plus_data_to_dict(cf['13'], qty, self.frame['bid_weight'])
                else:
                    self.add_data_to_dict(cf['13'], qty, self.frame['ask_trade_qty'])
                    self.plus_data_to_dict(cf['13'], qty, self.frame['ask_weight'])
                
                if qty * cf['13'] >= config.HIGHLIGHT_PRICE:
                    highlight_price.append((config.REALTIME_DATA, cf['13']))
            else:
                bid_spread_qty = self.frame['bid_spread_qty']
                ask_spread_qty = self.frame['ask_spread_qty']
                self.frame['bid_spread_qty'] = {}
                self.frame['ask_spread_qty'] = {}
                for p in config.BID_PAIR:
                    price = cf[p[0]]
                    qty = cf[p[1]]
                    h = self.compare_spread(bid_spread_qty, qty, price)
                    if h > 0:
                        highlight_price.append((config.BIDASK_DATA, h))
                    self.frame['bid_spread_qty'][price] = qty            
                for p in config.ASK_PAIR:
                    price = cf[p[0]]
                    qty = cf[p[1]]
                    h = self.compare_spread(ask_spread_qty, qty, price)
                    if h > 0:
                        highlight_price.append((config.BIDASK_DATA, h))
                    self.frame['ask_spread_qty'][price] = qty
        return highlight_price

    def get_data(self, price, col, role):
        if role == Qt.DisplayRole:
            if col == config.BID_TRADE_QTY_COL and price in self.frame['bid_trade_qty']:
                return sum(self.frame['bid_trade_qty'][price])
            elif col == config.BID_WEIGHT_COL and price in self.frame['bid_weight']:
                w = self.frame['bid_weight'][price] / self.frame['all_qty'] * 100.
                if w > 0.:
                    return '{0:0.1f}'.format(w)
            elif col == config.ASK_TRADE_QTY_COL and price in self.frame['ask_trade_qty']:
                return sum(self.frame['ask_trade_qty'][price])
            elif col == config.ASK_WEIGHT_COL and price in self.frame['ask_weight']:
                w = self.frame['ask_weight'][price] / self.frame['all_qty'] * 100.
                if w > 0.:
                    return '{0:0.1f}'.format(w)
            elif col == config.BID_SPREAD_QTY_COL and price in self.frame['bid_spread_qty']:
                return self.frame['bid_spread_qty'][price]
            elif col == config.ASK_SPREAD_QTY_COL and price in self.frame['ask_spread_qty']:
                return self.frame['ask_spread_qty'][price]
            
            return None
            
        return None