from datetime import datetime
import pandas as pd


class DayProfitCompareAccount:
    def __init__(self, option_name):
        self.option = 0
        self.option_name = option_name

        self.date = datetime.now().date()
        self.df = pd.DataFrame(columns = ['date', option_name, 'code', 'max_profit'])
        self.option_set = set()

    def set_up(self, c, d):
        self.option = c
        self.option_set.add(c)
        self.date = d

    def get_highest_price(self, date, code, price):
        from morning.cybos_api import stock_chart
        l, data = stock_chart.get_day_period_data(code, date, date)
        if l == 1:
            return data[0]['3']
        return price

    def summary(self):
        self.df.to_excel(self.option_name + '.xlsx')
        for c in self.option_set:
            print(c, 'AVG PROFIT', self.df[self.df[self.option_name] == c]['max_profit'].mean())

    def transaction(self, msg):
        _, code, trade, price, _ = str(msg).split(':')
        price = float(price)
        if trade == 'BUY':
            if self.date is not None:
                highest_price = self.get_highest_price(self.date, code, price)
                row = {'date': self.date, self.option_name: self.option,
                        'code': code, 'max_profit': (highest_price - price) / price * 100}
                self.df = self.df.append(row, ignore_index = True)
            else:
                row = {'date': datetime.now(), self.option_name: self.option,
                        'code': code, 'max_profit': price}
                self.df = self.df.append(row, ignore_index = True)