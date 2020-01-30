from datetime import datetime
import gevent

from morning_server import stock_api
from clients.mavg_trader import trader_env
from morning.pipeline.converter import dt


_trade_account = None
TRADE_SIMULATION = trader_env.USE_FAKE_ACCOUNT


class ProcessOrder:
    NONE=0
    IMMEDIATE=1
    END_MARKET=2

    def __init__(self, reader, code, is_buy, quantity=0):
        self.reader = reader
        self.code = code
        self.is_buy = is_buy
        self.type = ProcessOrder.NONE
        self.order_done = False
        self.quantity = quantity
        self.bid_ask_datas = []
        self.timer_started = False

    def time_check(self):
        while not self.order_done:
            gevent.sleep(5)
            self.bidask_data([])

    def process_buy(self, code, price):
        invest = stock_api.stock_api.get_balance()['balance'] / 10
        quantity = int(invest / price)
        if quantity == 0: #TODO: put log
            return
        else:
            stock_api.order_stock(self.reader, self.code, price, quantity, True)

    def process_sell(self, code, price, quantity):
        stock_api.order_stock(self.reader, self.code, price, quantity, False)

    def bidask_data(self, datas):
        if self.order_done:
            return

        ba_data = []
        for ba in datas:
            ba_data.append(dt.cybos_stock_ba_tick_convert(ba))
        if len(ba_data) > 0:
            data = ba_data[0]
            bid_prices = [data['first_bid_price'], data['second_bid_price'], data['third_bid_price']]
            ask_prices = [data['first_ask_price'], data['second_ask_price'], data['third_ask_price']]
            if not any(bid_prices) or not any(ask_prices):
                print('BID/ASK Price is zero', bid_prices, ask_prices)
                return
            else:
                bid_price = bid_prices[1]
                if bid_price == 0:
                    bid_price = bid_prices[0]
                ask_price = ask_prices[1]
                if ask_price == 0:
                    ask_price = ask_prices[0]

                if self.type == ProcessOrder.END_MARKET:
                    self.bid_ask_datas.append((bid_price, ask_price))

        if len(self.bid_ask_datas) == 0:
            return

        if self.type == ProcessOrder.IMMEDIATE:
            if self.is_buy:
                self.process_buy(self.code, self.bid_ask_datas[-1][1]) 
            else: 
                self.process_sell(self.code, self.bid_ask_datas[-1][0], self.quantity)
            self.order_done = True
        elif self.type == ProcessOrder.END_MARKET:
            now = datetime.now()
            if now.hour == trader_env.CLOSE_HOUR and now.minute == trader_env.CLOSE_ORDER_MINUTE:
                if self.is_buy:
                    self.process_buy(self.code, self.bid_ask_datas[-1][1])
                else:
                    self.process_sell(self.code, self.bid_ask_datas[-1][0], self.quantity)
                self.order_done = True

            if not self.timer_started:
                self.timer_started = True
                gevent.spawn(self.time_check)
            

    def process_order(self):
        now = datetime.now()
        if (trader_env.OPEN_HOUR <= now.hour <= trader_env.CLOSE_HOUR and
                                    now.minute < trader_env.CLOSE_MINUTE):
            self.type = ProcessOrder.IMMEDIATE
        elif now.hour == trader_env.CLOSE_HOUR and now.minute < trader_env.CLOSE_DONE_MINUTE:
            self.type = ProcessOrder.END_MARKET
        else:
            print('Cannot process order(timeerror')
            return
        stock_api.subscribe_stock_bidask(self.reader, self.code, self.bidask_data)


class TradeAccount:
    def GetAccount(message_reader = None):
        global _trade_account
        if _trade_account is None:
            _trade_account = TradeAccount(message_reader, TRADE_SIMULATION)
        return _trade_account

    def __init__(self, message_reader, is_simulation):
        self.is_simulation = is_simulation
        self.message_reader = message_reader

        self.trade_list = []
        if self.is_simulation:
            # key: code, value: {'price', sell_available', 'buy_date', 'sell_price', 'sell_date'}
            self.balance = 10000000
            self.long_list = dict()
        else: # subscribe trade result
            stock_api.subscribe_trade(self.message_reader, self.trade_result)

    def trade_result(self, result):
        print(result)
        #TODO: how to handle?

    def get_balance(self):
        if self.is_simulation:
            return self.balance
        else:
            return stock_api.get_balance()['balance']

    def set_balance(self, balance):
        self.balance = balance

    def buy_stock(self, code):
        # do not get balance here since every order will get same amounts
        self.trade_list.append(ProcessOrder(self.message_reader, code, True)) 

    def sell_stock(self, quantity, code):
        self.trade_list.append(ProcessOrder(self.message_reader, code, False, quantity)) 

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
