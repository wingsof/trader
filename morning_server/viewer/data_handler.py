from PyQt5.QtCore import QObject, pyqtSlot
from datetime import datetime, timedelta, time

from morning.back_data import holidays
from morning_server import stock_api
from morning.pipeline.converter import dt
from utils import time_converter
from morning_server.viewer import figure
import numpy as np
from morning_server.viewer import edgefinder

message_reader = None

class DataHandler(QObject):
    NEW_DATA = 0
    
    def __init__(self):
        super().__init__()
        self.current_code = 'A000000'
        self.current_dt = None
        self.yesterday = None
        self.today = None
        self.yesterday_min_data_c = []
        self.today_min_data_c = []
        self.figure = figure.Figure()
        self.volume_average = 0
        self.moving_average = []
        self.average_data = []
        self.up_to = None
        self.price_range = [0, 0]

    def get_figure(self):
        return self.figure

    def clear_datas(self):
        self.yesterday_min_data_c.clear()
        self.today_min_data_c.clear()
        self.average_data.clear()
        self.moving_average.clear()
        self.price_range = [0, 0]

    def calc_moving_average(self, yesterday_min, today_min):
        data = np.array([(self.convert_to_timestamp(ym['0'], ym['time']), ym['close_price']) for ym in yesterday_min]) 
        data = np.r_[data, [(self.convert_to_timestamp(tm['0'], tm['time']), tm['close_price']) for tm in today_min]]
        price_array = np.array([])
        for d in data:
            price_array = np.append(price_array, [d[1]])
            if len(price_array) < 10:
                self.moving_average.append((d[0], price_array.mean()))
            else:
                self.moving_average.append((d[0], price_array[-10:].mean()))


    def set_figure_data(self, up_to):
        up_to_data = []
        up_to_moving_average = []
        volume_max = max([d['volume'] for d in self.average_data])

        for ad in self.average_data:
            if ad['time'] > up_to.timestamp() * 1000:
                break
            else:
                up_to_data.append(ad)
        
        for ma in self.moving_average:
            if ma[0] > up_to.timestamp() * 1000:
                break
            else:
                up_to_moving_average.append(ma)

        ef = edgefinder.EdgeFinder(up_to_moving_average)
        peaks_top = ef.get_peaks(True)
        peaks_bottom = ef.get_peaks(False)
        summary = {'today': datetime.combine(self.today, time()), 'yesterday': datetime.combine(self.yesterday, time()),
                    'price_min': self.price_range[0], 'price_max': self.price_range[1], 'volume_max': volume_max, 'volume_average': self.volume_average,
                    'data': up_to_data, 'moving_average': up_to_moving_average, 'peak_top': peaks_top, 'peak_bottom': peaks_bottom}

        self.figure.set_display_data(summary)


    def load_data(self, code, target_date):
        yesterday = holidays.get_yesterday(target_date)
        yesterday_min_data = stock_api.request_stock_minute_data(message_reader, code, yesterday, yesterday)
        if len(yesterday_min_data) <= 10:
            print('NO or LESS YESTERDAY MIN DATA', code, yesterday)
            return
        today_min_data = stock_api.request_stock_minute_data(message_reader, code, target_date, target_date)
        if len(today_min_data) <= 10:
            print('NO or LESS TODAY MIN DATA', code, target_date)
            return

        past_datas = stock_api.request_stock_day_data(message_reader, code, yesterday - timedelta(days=30), yesterday)
        if len(past_datas) <= 10:
            print('NO or LESS PAST DATA', code,  yesterday - timedelta(days=30), yesterday)
            return
        
        self.yesterday = yesterday
        self.today = target_date

        vol = 0
        for d in past_datas:
            vol += d['6']
        self.volume_average = int(vol / len(past_datas))

        self.clear_datas()
        yesterday_min_close = yesterday_min_data[-1]['5']
        self.price_range[0] = yesterday_min_close - int(yesterday_min_close * 0.1)
        self.price_range[1] = yesterday_min_close + int(yesterday_min_close * 0.1)

        for ym in yesterday_min_data:
            if ym['4'] < self.price_range[0]:
                self.price_range[0] = ym['4']
            if ym['3'] > self.price_range[1]:
                self.price_range[1] = ym['3']
            self.yesterday_min_data_c.append(dt.cybos_stock_day_tick_convert(ym))

        for tm in today_min_data:
            if tm['4'] < self.price_range[0]:
                self.price_range[0] = tm['4']
            if tm['3'] > self.price_range[1]:
                self.price_range[1] = tm['3']
            self.today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))

        self.calc_moving_average(self.yesterday_min_data_c, self.today_min_data_c)

        yesterday_average = self.create_average_data(yesterday, self.yesterday_min_data_c)
        today_average = self.create_average_data(target_date, self.today_min_data_c)
        self.average_data.extend(yesterday_average)
        self.average_data.extend(today_average)

        self.up_to = datetime.combine(yesterday, time(12))
        self.set_figure_data(self.up_to)

    def convert_to_timestamp(self, record_date, record_time):
        return self.convert_to_datetime(record_date, record_time).timestamp() * 1000

    def convert_to_datetime(self, record_date, record_time):
        hour_min = time_converter.intdate_to_datetime(record_date)
        hour_min = hour_min.replace(hour=int(record_time / 100), minute=int(record_time % 100))
        return hour_min

    def create_average_data(self, target_date, data):
        MAVG_STEP = 10
        start_hour_min = self.convert_to_datetime(data[0]['0'], 900)
        finish_hour_min = self.convert_to_datetime(data[0]['0'], 1530)
        data = data.copy()
        new_data = []
        time_category = []
        o, l, c, h, v = 0, 0, 0, 0, 0
        
        while start_hour_min < finish_hour_min and len(data) > 0:
            d = data[0]
            data_datetime = self.convert_to_datetime(d['0'], d['time'])
            while data_datetime <= start_hour_min + timedelta(minutes=MAVG_STEP):
                if h == 0:
                    o, l, c, h, v = d['start_price'], d['lowest_price'], d['close_price'], d['highest_price'], d['volume']
                else:
                    c = d['close_price']
                    l = d['lowest_price'] if d['lowest_price'] < l else l
                    h = d['highest_price'] if d['highest_price'] > h else h
                    v += d['volume']

                data.pop(0)
                if len(data) > 0:
                    d = data[0]
                    data_datetime = self.convert_to_datetime(d['0'], d['time'])
                else:
                    break

            start_hour_min += timedelta(minutes=MAVG_STEP)
            time_category.append(start_hour_min.strftime('%H:%M'))
            new_data.append({'start_price': o,
                            'lowest_price': l,
                            'highest_price': h,
                            'close_price': c,
                            'volume': v,
                            'time': start_hour_min.timestamp() * 1000})
            o, l, c, h, v = 0, 0, 0, 0, 0
        return new_data

    @pyqtSlot(str, datetime)
    def info_changed(self, code, d):
        if holidays.is_holidays(d):
            # TODO: displaying Popup
            print('Holiday')
            return
        if self.current_code == code and self.current_dt == d:
            return
        self.current_code = code
        self.current_dt = d
        if len(code) == 0:
            # TODO: Pick one randomly
            pass
        else:
            self.load_data(code, d)
        

    @pyqtSlot()
    def check_next(self):
        # TODO: Step1: Show datas until PM 12:00
        #       Step2: Show datas until find peak (up to today)
        pass

