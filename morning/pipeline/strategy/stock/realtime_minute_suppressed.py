from morning.pipeline.strategy.stock.minute_suppressed import MinuteSuppressed
from datetime import datetime, timedelta
from morning.logging import logger

class RealtimeMinuteSuppressed:
    # Reuse MinuteSuppressed for preventing to make mistakes
    # Purpose is a converting realtime data to minute data
    def __init__(self):
        self.next_element = None
        self.ms = MinuteSuppressed()
        self.ms_wrapper = self._MinuteSuppressedWrapper(self.signal_received)
        self.ms.set_output(self.ms_wrapper)
        self.current_datetime = None
        self.tick_prices = []

    def add_graph(self, _):
        pass

    def signal_received(self, msg):
        if self.next_element is not None:
            self.next_element.received(msg)

    def set_output(self, next_ele):
        self.next_element = next_ele

    def received(self, datas):
        for d in datas:
            current = d['date']

            if self.current_datetime is None:
                self.current_datetime = current

            if current - self.current_datetime > timedelta(minutes=1):
                dt = self.current_datetime
                self.tick_prices.append(d['current_price'])
                year, month, day, hour, minute = dt.year, dt.month, dt.day, dt.hour, dt.minute
                min_data = {'date': datetime(year, month, day, hour, minute), 
                            'cum_buy_volume': d['cum_buy_volume'],
                            'cum_sell_volume': d['cum_sell_volume'], 
                            'close_price': d['current_price'], 
                            'start_price': self.tick_prices[0],
                            'highest_price': max(self.tick_prices),
                            'lowest_price': min(self.tick_prices),
                            'stream': d['stream'],
                            'target': d['target']}
                self.tick_prices.clear()
                self.ms.received([min_data])
                self.current_datetime = d['date']
            else:
                self.tick_prices.append(d['current_price'])

    def finalize(self):
        if self.next_element:
            self.next_element.finalize()


    class _MinuteSuppressedWrapper:
        def __init__(self, callback):
            self.callback = callback

        def received(self, msg):
            self.callback(msg)