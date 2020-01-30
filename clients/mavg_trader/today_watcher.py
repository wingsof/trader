from datetime import datetime, date, time
import gevent

from morning_server import stock_api
from morning_server import message
from morning.pipeline.converter import dt
from clients.mavg_trader import trade_account
from clients.mavg_trader import tick_data
from clients.mavg_trader import trader_env

today_traders = []

class TodayTrader:
    def __init__(self, code, code_info, today, position):
        self.code = code
        self.code_info = code_info
        self.today = today
        self.position = position
        self.open_price = 0
        self.close_time = datetime(today.year, today.month, today.day, trader_env.CLOSE_HOUR, trader_env.CLOSE_MINUTE)
        self.today_data = []
        self.highest_price = 0
        self.buy_zone = False
        self.sell_zone = False
        self.sell_trace = False
        self.trade_done = False
        self.tick_data = None

        self.simulation = False
        # temporary for testing
        self.simulation = True

    def set_simulation_data(self, data):
        self.simulation = True
        self.data = data

    def process_buy(self, data):
        if data is None and len(self.today_data) == 0:
            return

        if self.buy_zone:
            if self.simulation:
                trade_account.TradeAccount.GetAccount().buy_stock_by_minute_data(self.code, data, self.today)
            else:
                trade_account.TradeAccount.GetAccount().buy_stock(self.code)
            print('================BUY', self.code, self.today)
            self.trade_done = True
        elif data is None:
            today_increase = self.today_data[-1]['close_price'] >= self.open_price
            today_over_bull = (self.highest_price - self.code_info.yesterday_data['close_price']) / self.code_info.yesterday_data['close_price'] * 100 >= 10
            over_cut = self.today_data[-1]['close_price'] >= self.code_info.cut
            #print(self.code, today_increase, today_over_bull, over_cut, self.code_info.cut, self.today_data[-1]['close_price'])
            if today_increase and not today_over_bull and over_cut:
                self.buy_zone = True
        else:
            self.today_data.append(data)
            if self.highest_price < data['highest_price']:
                self.highest_price = data['highest_price']

    def process_sell(self, data):
        if data is None and len(self.today_data) == 0:
            return

        if self.sell_zone:
            if self.simulation:
                trade_account.TradeAccount.GetAccount().sell_stock_by_minute_data(self.code, data, self.today)
            else:
                trade_account.TradeAccount.GetAccount().sell_stock(self.code, self.code_info.sell_available)
            self.trade_done = True
            print('================SELL', self.code, self.today)
        elif data is None:
            if self.sell_trace:
                self.sell_zone = True
        else:
            is_above_mavg = self.code_info.yesterday_data['moving_average'] < data['close_price']

            if self.sell_trace:
                if (data['close_price'] - data['highest_price']) / data['highest_price'] * 100. < -4 or not is_above_mavg:
                    self.sell_zone = True
            else:
                today_profit = (data['close_price'] - self.code_info.yesterday_data['close_price']) / self.code_info.yesterday_data['close_price'] * 100
                current_profit = (data['close_price'] - self.open_price) / self.open_price * 100
                #print('SELL candidate', today_profit, current_profit, is_above_mavg)
                if today_profit > 25 or not is_above_mavg:
                    self.sell_zone = True
                elif abs(current_profit) > 9:
                    self.sell_trace = True

    def process_minute(self, data):
        if self.trade_done:
            return

        if data is None:
            pass
        elif self.open_price == 0:
            self.open_price = data['start_price']

        if self.position == trader_env.STATE_OVER_AVG:
            self.process_buy(data)
        else:
            self.process_sell(data)

    def tick_handler(self, code, datas):
        if self.tick_data is None:
            self.tick_data = tick_data.TickData(self.today)
        self.tick_data.add_tick_data(datas, self.process_minute)
    
    def close_check(self):
        while True:
            print('CLOSE_CHECK', self.close_time, datetime.now())
            if self.close_time <= datetime.now():
                break
            elif self.tick_data is not None:
                # below will prevent not to stay longer when no tick data for a while
                self.tick_data.create_minute_data(self.process_minute)
            gevent.sleep(5)
        self.process_minute(None) 

    def start_timer(self):
        gevent.spawn(self.close_check)

    def start(self):
        # running entry for simulation
        if len(self.data) == 0:
            return
        for d in self.data[:-1]:
            self.process_minute(d)
        self.process_minute(None)
        self.process_minute(self.data[-1])


def add_watcher(reader, code, code_info, today, state, is_simulation):
    tt = None
    if not is_simulation:
        tt = TodayTrader(code, code_info, today, state)
        stock_api.subscribe_stock(reader, code, tt.tick_handler)
        tt.start_timer()
    else:
        tt = TodayTrader(code, code_info, today, state)
        today_data = stock_api.request_stock_minute_data(reader, code, today, today)
        today_min_data = []
        for td in today_data:
            today_min_data.append(dt.cybos_stock_day_tick_convert(td))
        #print('data len', len(today_min_data))
        tt.set_simulation_data(today_min_data)
        tt.start()

    today_traders.append(tt)
