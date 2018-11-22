import win32com.client
from PyQt5 import QtCore

class _CpEvent:
    NONE = 0
    BUY = 1
    SELL = 2

    def set_params(self, obj, code, position, buy_price, sell_price, profit_e, current_obj):
        self.obj = obj
        self.status = _CpEvent.NONE
        self.code = code
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.is_long = position
        self.current_obj = current_obj
        self.profit_expected = profit_e
        self.highest_buy_after_hour = 0
        self.lowest_sell_after_hour = 10000000

    def OnReceived(self):
        price = self.obj.GetHeaderValue(13)

        if self.obj.GetHeaderValue(20) == ord('2') and self.obj.GetHeaderValue(3) <= 1520: # 09:00, 15:30
            if self.status is _CpEvent.NONE:
                if self.is_long:
                    if price <= self.sell_price:
                        self.status = _CpEvent.SELL
                        self.current_obj.add_to_sell_cart(self.code)
                else:
                    if price >= self.buy_price:
                        self.status = _CpEvent.BUY
                        self.current_obj.add_to_buy_cart(self.code, self.profit_expected)

        elif self.status is not _CpEvent.NONE and self.obj.GetHeaderValue(20) == ord('5'): # 15:20-15:30
            if self.status is _CpEvent.BUY and self.obj.GetHeaderValue(14) == ord('1'):
                if price > self.highest_buy_after_hour:
                    self.highest_buy_after_hour = price
                    self.current_obj.set_buy_price(self.code, price)
            elif self.status is _CpEvent.SELL and self.obj.GetHeaderValue(14) == ord('2'):
                if price < self.lowest_sell_after_hour:
                    self.lowest_sell_after_hour = price
                    self.current_obj.set_sell_price(self.code, price)


class _StockRealtime:
    def __init__(self, code, is_long, info, current_obj):
        self.obj = win32com.client.Dispatch('DsCbo1.StockCur')
        self.code = code
        self.is_long = is_long
        self.info = info 
        self.current_obj = current_obj

    def subscribe(self):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.code, self.is_long, 
                self.info['prev_close'] + self.info['prev_close'] * self.info['buy_rate'],
                self.info['prev_close'] - self.info['prev_close'] * self.info['sell_rate'],
                self.info['profit_expected'], self.current_obj)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class StockCurrent:
    def __init__(self, code_list, long_codes, speculation):
        self.code_list = code_list
        self.long_codes = long_codes
        self.realtime_bucket = []
        self.buy_dict = {}
        self.sell_dict = {}

        for code in self.code_list:
            row = speculation[speculation['code'] == code].iloc[0]
            self.realtime_bucket.append(_StockRealtime(code, code in self.long_codes, row, self))

    def stop(self):
        for r in self.realtime_bucket:
            r.unsubscribe()

    def start(self):
        for r in self.realtime_bucket:
            r.subscribe()

    def add_to_buy_cart(self, code, expected):
        if expected: > 105.
            print('BUY CART(%d)' % len(self.buy_dict), code, expected)
            self.buy_dict[code] = [expected, 0]

    def add_to_sell_cart(self, code):
        print('SELL CART(%d)' % len(self.sell_dict), code)
        self.sell_dict[code] = [0, 0]

    def set_sell_price(self, code, price):
        self.sell_dict[code][1] = price
    
    def set_buy_price(self, code, price):
        self.buy_dict[code][1] = price

    def get_buy_dict(self):
        return self.buy_dict

    def get_sell_dict(self):
        return self.sell_dict
