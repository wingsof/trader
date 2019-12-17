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
        self.ticks = []
        self.is_first_tick = True
        self.is_vi = False

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

            if (current.hour >= 9 and current.minute > 2) and (current.hour <=15 and current.minute < 20) and d['market_type'] == ord('1'):
                self.is_vi = True
            else:
                self.is_vi = False

            if current.minute != self.current_datetime.minute:
                dt = self.current_datetime
                year, month, day, hour, minute = dt.year, dt.month, dt.day, dt.hour, dt.minute
                if len(self.ticks) == 0:
                    logger.error('ticks len is 0', d['target'], current.minute, self.current_datetime.minute)
                else:
                    start_price = self.ticks[0]['current_price']
                    if self.is_first_tick:
                        self.is_first_tick = False
                        start_price = self.ticks[0]['current_price'] - self.ticks[0]['yesterday_diff']

                    min_data = {'date': datetime(year, month, day, hour, minute),
                                'volume': sum([t['volume'] for t in self.ticks]),
                                'cum_buy_volume': self.ticks[-1]['cum_buy_volume'], # currently just use current vol
                                'cum_sell_volume': self.ticks[-1]['cum_sell_volume'], # currently just use current vol
                                'close_price': self.ticks[-1]['current_price'],
                                'start_price': start_price,
                                'highest_price': max([t['current_price'] for t in self.ticks]),
                                'lowest_price': min([t['current_price'] for t in self.ticks]),
                                'VI': self.is_vi,
                                'stream': d['stream'],
                                'target': d['target']}
                    self.ticks.clear()
                    self.ms.received([min_data])
                    self.current_datetime = d['date']

            self.ticks.append(d)

    def finalize(self):
        if self.next_element:
            self.next_element.finalize()


    class _MinuteSuppressedWrapper:
        def __init__(self, callback):
            self.callback = callback

        def received(self, msg):
            self.callback(msg)
