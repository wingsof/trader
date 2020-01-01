from PyQt5.QtCore import QObject, pyqtSlot
from datetime import datetime

from morning.back_data import holidays
from morning_server import stock_api
from morning.pipeline.converter import dt
import figure

message_reader = None

class DataHandler(QObject):
    NEW_DATA = 0
    
    def __init__(self):
        super().__init__()
        self.current_code = 'A000000'
        self.current_dt = None
        self.yesterday_min_data_c = []
        self.today_min_data_c = []
        self.figure = figure.Figure()

    def get_figure(self):
        return self.figure

    def load_data(self, code, target_date):
        yesterday = holidays.get_yesterday(target_date)
        yesterday_min_data = stock_api.request_stock_minute_data(message_reader, code, yesterday, yesterday)
        if len(yesterday_min_data) <= 10:
            print('NO or LESS YESTERDAY MIN DATA', code, yesterday)
            return
        today_min_data = stock_api.request_stock_minute_data(message_reader, code, target_date, target_date)
        if len(today_min_data) <= 10:
            print('NO or LESS TODAY MIN DATA', code, d)
            return

        self.yesterday_min_data_c.clear()
        self.today_min_data_c.clear()

        for ym in yesterday_min_data:
            self.yesterday_min_data_c.append(dt.cybos_stock_day_tick_convert(ym))

        for tm in today_min_data:
            self.today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))
        self.figure.set_data(yesterday, target_date, self.yesterday_min_data_c, self.today_min_data_c)


    @pyqtSlot(str, datetime)
    def info_changed(self, code, d):
        if holidays.is_holidays(d):
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
        pass