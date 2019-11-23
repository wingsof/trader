import pandas as pd
from morning.logging import logger


class FakeAccount:
    def __init__(self):
        self.amount = 10000000
        self.account = {}
        self.df = pd.DataFrame(columns=['time', 'vendor', 'code', 'trade', 'price', 'profit'])

    def transaction(self, msg):
        # Investing 1 / 10 amount
        logger.print(str(msg))
        vendor, code, trade, price, time = str(msg).split(':')
        price = int(price)
        
        profit = 0
        if trade == 'BUY':
            self.account[code] = price
        else:
            profit = price - self.account[code]

        data = {'time': time, 'vendor':vendor, 'code': code, 'trade': trade, 'price': price, 'profit': profit}
        self.df = self.df.append(data, ignore_index = True)
        self.df.to_excel('account.xlsx')
        # vendor:target:BUY:ask_price 
        # vendor:target:SELL:bid_price 
