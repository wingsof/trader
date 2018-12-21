import config
from PyQt5.QtCore import Qt


class BeforeMarket:
    def __init__(self, price_list):
        self.price_list = price_list
        self.bid_qty = {}
        self.ask_qty = {}
        self.bid_weight = {}
        self.ask_weight = {}
        self.all_qty = 0

    def handle_data(self, sec_data):
        self.bid_qty = {}
        self.ask_qty = {}
        for data in sec_data:
            if data['17'] > 0:  # quantity
                self.all_qty += data['17']
                if data['26'] == ord('1'): # bid
                    self.bid_qty[data['13']] = data['17']
                    self.bid_weight[data['13']] += data['17']
                elif data['26'] == ord('2'): # ask
                    self.ask_qty[data['13']] = data['17']
                    self.ask_weight[data['13']] += data['17']

    def get_data(self, price, col, role):
        if role == Qt.DisplayRole:
            if col == config.BID_QTY_COL and price in self.bid_qty:
                return self.bid_qty[price]
            elif col == config.BID_WEIGHT_COL and price in self.bid_weight:
                return self.bid_weight[price] / self.all_qty * 100.
            elif col == config.ASK_QTY_COL and price in self.ask_qty:
                return self.ask_qty[price]
            elif col == config.ASK_WEIGHT_COL and price in self.ask_weight:
                return self.ask_weight[price] / self.all_qty * 100.
            
            return None
            
        return None