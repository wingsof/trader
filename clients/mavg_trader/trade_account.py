from morning_server import stock_api


_trade_account = None
TRADE_SIMULATION = False

class TradeAccount:
    def GetAccount():
        global _trade_account
        if _trade_account is None:
            _trade_account = TradeAccount(TRADE_SIMULATION)
        return _trade_account

    def __init__(self, is_simulation):
        self.is_simulation = is_simulation


        if self.is_simulation:
            # only for simulation key: code, value: {'price', sell_available', 'buy_date', 'sell_price', 'sell_date'}
            self.balance = 10000000
            self.long_list = dict()
            self.trade_list = []
        else:
            self.balance = stock_api.get_balance()['balance']

    def buy_stock(self, code):
        pass

    def sell_stock(self, code):
        pass

    def buy_stock_by_minute_data(self, code, minute_data, today):
        invest = self.balance / 10
        quantity = invest / minute_data['close_price']
        if int(quantity) < 1:
            print('Failed to trade', invest, self.balance)
            return
        self.balance = self.balance - (minute_data['close_price'] * int(quantity))
        self.long_list[code] = {'price': minute_data['close_price'], 'sell_available': int(quantity), 'buy_date': today}

    def sell_stock_by_minute_data(self, code, minute_data, today):
        amount = minute_data['close_price'] * self.long_list[code]['sell_available']
        self.balance += amount
        trade_data = self.long_list[code]
        trade_data['code'] = code
        trade_data['sell_price'] = minute_data['close_price']
        trade_data['sell_date'] = today
        trade_data['profit'] = (minute_data['close_price'] - trade_data['price']) / trade_data['price'] * 100
        self.trade_list.append(trade_data)
        self.long_list.pop(code, None)

    def get_long_list(self):
        return self.long_list
    
    def get_trade_list(self):
        return self.trade_list

    def __str__(self):
        return 'LONG LIST\n' + str(self.long_list) + '\nTRADE LIST\n' + str(self.trade_list)
