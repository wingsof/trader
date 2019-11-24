import pandas as pd
from datetime import datetime
#from morning.logging import logger


class FakeAccount:
    def __init__(self, save_to_file = '', fresh_daily = True):
        self.amount = 10000000
        self.account = {}
        self.save_to_file = save_to_file
        self.date = datetime.now().date()
        self.day_profit = 0
        self.df = pd.DataFrame(columns=['date', 'time', 'vendor', 'code', 'trade', 'price', 'profit'])
        self.profit_df = pd.DataFrame(columns=['date', 'code', 'profit', 'profit_r'])

    def set_date(self, d):
        self.date = d
        self.day_profit = 0

    def summary(self):
        print(self.profit_df)
        self.df.to_excel('account.xlsx')
        self.profit_df.to_excel('summary.xlsx')
        

    def transaction(self, msg):
        # Investing 1 / 10 amount
        #logger.print(str(msg))
        vendor, code, trade, price, time = str(msg).split(':')
        price = int(price)
        
        profit = 0
        if trade == 'BUY':
            self.account[code] = price
        else:
            vol = (self.amount / 10) / self.account[code]
            remain = (price * vol) - (self.account[code] * vol)
            self.day_profit += remain
            profit = remain / (self.amount / 10) * 100.
            profit_d = {'date': self.date, 'code': code, 'profit': remain, 'profit_r': profit}
            self.profit_df = self.profit_df.append(profit_d, ignore_index = True)
            

        data = {'date': self.date, 'time': time, 'vendor':vendor, 'code': code, 'trade': trade, 'price': price, 'profit': profit}
        self.df = self.df.append(data, ignore_index = True)
        #self.df.to_excel('account.xlsx')
        # vendor:target:BUY:ask_price:time
        # vendor:target:SELL:bid_price:time
