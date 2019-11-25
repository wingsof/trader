from datetime import datetime
import pandas as pd


class DayProfitCompareAccount:
    def __init__(self, save_to_file = ''):
        self.start_up_count = 3
        self.date = datetime.now().date()
        self.df = pd.DataFrame(columns = ['date', 'startup', 'code', 'max_profit'])
        self.start_ups = set()

    def set_up(self, c, d):
        self.start_up_count = c
        self.start_ups.add(c)
        self.date = d

    def get_highest_price(self, date, code, price):
        from morning.cybos_api import stock_chart
        l, data = stock_chart.get_day_period_data(code, date, date)
        if l == 1:
            return data[0]['3']
        return price

    def summary(self):
        self.df.to_excel('start_up.xlsx')
        for c in self.start_ups:
            print(c, 'AVG PROFIT', self.df[self.df['startup'] == c]['max_profit'].mean())

    def transaction(self, msg):
        _, code, trade, price, _ = str(msg).split(':')
        price = int(price)
        if trade == 'BUY':
            highest_price = self.get_highest_price(self.date, code, price)
            row = {'date': self.date, 'startup': self.start_up_count,
                    'code': code, 'max_profit': (highest_price - price) / price * 100}
            self.df = self.df.append(row, ignore_index = True)