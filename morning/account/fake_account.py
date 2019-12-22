import pandas as pd
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSlot

from morning.logging import logger


class FakeAccount(QObject):
    def __init__(self, save_to_file = '', fresh_daily = True):
        super().__init__()
        self.account = dict()
        self.save_to_file = save_to_file
        self.date = datetime.now().date()
        self.additional_info = []
        self.profit_df = pd.DataFrame(columns=['date', 'code', 'buy_price', 'sell_price', 'profit_r', 'buy_time', 'sell_time'])

    def set_date(self, d):
        self.date = d

    def summary(self):
        print(self.profit_df)
        self.profit_df.to_excel('profit_' + self.save_to_file + '.xlsx')
    
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
            profit = (price - self.account[code]['price']) / self.account[code]['price'] * 100.
            profit_d = {'date': self.date, 'code': code, 'buy_price': self.account[code]['price'], 'sell_price': price,
                        'profit_r': profit, 'buy_time': self.account[code]['date'], 'sell_time': tdate}
            if 'highest' in msg:
                profit_d['highest'] = msg['highest']

            for additional in self.additional_info:
                profit_d[additional[0]] = additional[1]
            self.profit_df = self.profit_df.append(profit_d, ignore_index = True)
            

        #data = {'date': self.date, 'code': code, 'trade': 'BUY' if buy else 'SELL', 'price': price, 'profit': profit}
