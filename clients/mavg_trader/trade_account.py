from morning_server import stock_api
from clients.mavg_trader import trader_env


_trade_account = None
TRADE_SIMULATION = trader_env.USE_FAKE_ACCOUNT

class TradeAccount:
    def GetAccount(message_reader = None):
        global _trade_account
        if _trade_account is None:
            _trade_account = TradeAccount(message_reader, TRADE_SIMULATION)
        return _trade_account

    def __init__(self, message_reader, is_simulation):
        self.is_simulation = is_simulation
        self.message_reader = message_reader

        if self.is_simulation:
            # only for simulation key: code, value: {'price', sell_available', 'buy_date', 'sell_price', 'sell_date'}
            self.balance = 10000000
            self.long_list = dict()
            self.trade_list = []

    def get_balance(self):
        if self.is_simulation:
            return self.balance
        else:
            return stock_api.get_balance()['balance']


    def set_balance(self, balance):
        self.balance = balance

    def buy_stock(self, code):
        invest = self.get_balance() / 10
        #stock_api.order_stock(self.message_reader, code, price, quantity, True)

    def sell_stock(self, code):
        #stock_api.order_stock(self.message_reader, code, price, quantity, False)
        pass

    def buy_stock_by_minute_data(self, code, minute_data, today):
        invest = self.get_balance() / 10
        quantity = invest / minute_data['close_price']
        if int(quantity) < 1:
            print('Failed to trade', invest, self.get_balance())
            return
        self.set_balance(self.get_balance() - (minute_data['close_price'] * int(quantity)))
        self.long_list[code] = {'price': minute_data['close_price'], 'sell_available': int(quantity), 'buy_date': today}

    def sell_stock_by_minute_data(self, code, minute_data, today):
        amount = minute_data['close_price'] * self.long_list[code]['sell_available']
        self.set_balance(self.get_balance() + amount)
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
        return 'TRADE LIST\n' + str(self.trade_list)
