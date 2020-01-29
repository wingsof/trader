from datetime import datetime, time, timedelta

from morning.pipeline.converter import dt
from clients.mavg_trader import trader_env


class TickData:
    def __init__(self, today):
        self.today = today
        self.close_time = datetime(today.year, today.month, today.day, trader_env.CLOSE_HOUR, trader_env.CLOSE_MINUTE)
        self.start_time = datetime(today.year, today.month, today.day, trader_env.OPEN_HOUR, trader_env.OPEN_MINUTE)
        self.in_market_data = []

    def add_tick_data(self, datas, minute_handler):
        tick_data = []

        for d in datas:
            tick_data.append(dt.cybos_stock_tick_convert(d))
        if len(tick_data) == 0:
            return
        elif len(tick_data) > 1:
            print('tick data len is over 1')
            
        data = tick_data[0]
        hour = int(data['time_with_sec'] / 10000)
        min = int(data['time_with_sec'] % 10000 / 100)
        second = int(data['time_with_sec'] % 100)
        data['date'] = datetime.combine(self.today, time(hour, min, second))

        if (data['market_type'] == dt.MarketType.IN_MARKET or
                (data['market_type'] == dt.MarketType.PRE_MARKET_EXP and
                    self.start_time <= data['date'] <= self.close_time)):
            self.in_market_data.append(data)
        self.create_minute_data(minute_handler)

    def pack_minute_data(self, data, handler):
        close_price = data[-1]['current_price']
        max_price = max([d['current_price'] for d in data])
        open_price = data[0]['current_price']
        minute_time = data[0]['time']
        min_data = {'time': minute_time,
            'close_price': close_price,
            'start_price': open_price,
            'highest_price': max_price}
        handler(min_data)

    def create_minute_data(self, handler):
        cut_index = -1
        cut_data = []

        if len(self.in_market_data) == 0:
            return

        data_time = self.in_market_data[0]['date'].minute
        for i, data in enumerate(self.in_market_data):
            if data['date'].minute != data_time:
                cut_index = i

        if cut_index == -1:
            if datetime.now() - self.in_market_data[-1]['date'] > timedelta(seconds=120):
                print('pack by timeout------------------------')
                self.pack_minute_data(self.in_market_data, handler)    
                self.in_market_data.clear()
        else:
            cut_count = cut_index + 1
            while cut_count > 0:
                cut_count -= 1   
                cut_data.append(self.in_market_data.pop(0))

            if len(cut_data) == 0:
                return

            self.pack_minute_data(cut_data, handler)
