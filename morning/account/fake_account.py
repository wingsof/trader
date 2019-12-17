import pandas as pd
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSlot

from morning.logging import logger


class FakeAccount(QObject):
    def __init__(self, save_to_file = '', fresh_daily = True):
        super().__init__()
        self.amount = 10000000
        self.account = {}
        self.save_to_file = save_to_file
        self.date = datetime.now().date()
        self.day_profit = 0
        self.additional_info = []
        self.df = pd.DataFrame(columns=['date', 'code', 'trade', 'price', 'profit'])
        self.profit_df = pd.DataFrame(columns=['date', 'code', 'profit', 'profit_r', 'buy_time', 'sell_time'])

    def set_date(self, d):
        self.date = d
        self.day_profit = 0

    def summary(self):
        print(self.profit_df)
        self.df.to_excel('account.xlsx')
        self.profit_df.to_excel('summary.xlsx')
    
    def clear_additional_info(self):
        self.additional_info.clear()

    def add_additional_info(self, name, value):
        self.additional_info.append((name, value))

    @pyqtSlot(object)
    def transaction(self, msg):
        # Investing 1 / 10 amount
        logger.print(str(msg))
        buy, code, price, tdate = msg['result'], msg['target'], msg['value'], msg['date']
        price = int(price)

        profit = 0
        if buy:
            self.account[code] = dict(price=price, date=tdate)
        else:
            vol = (self.amount / 10) / self.account[code]['price']
            remain = (price * vol) - (self.account[code]['price'] * vol)
            self.day_profit += remain
            profit = remain / (self.amount / 10) * 100.
            profit_d = {'date': self.date, 'code': code, 
                        'profit': remain, 'profit_r': profit, 
                        'buy_time': self.account[code]['date'], 'sell_time': tdate}
            for additional in self.additional_info:
                profit_d[additional[0]] = additional[1]
            self.profit_df = self.profit_df.append(profit_d, ignore_index = True)
            

        data = {'date': self.date, 'code': code, 'trade': 'BUY' if buy else 'SELL', 'price': price, 'profit': profit}
        self.df = self.df.append(data, ignore_index = True)
        #self.df.to_excel('account.xlsx')
        # vendor:target:BUY:ask_price:time
        # vendor:target:SELL:bid_price:time
