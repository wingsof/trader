from PyQt5.QtWidgets import QGridLayout, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import QTimer, QDateTime, QDate, QTime, Qt
from PyQt5.QtChart import QChart, QLineSeries, QCandlestickSeries, QChartView, QDateTimeAxis, QValueAxis, QCandlestickSet, QScatterSeries
from datetime import time, datetime, timedelta
from utils import time_converter
import numpy as np
import random
import math


class PriceFigure:
    def __init__(self, name):
        self.name = name
        self.chart_view = QChartView()

        self.price_time_axis = QDateTimeAxis()
        self.price_time_axis.setFormat('h:mm')

        self.price_axis = QValueAxis()
        self.candle_stick_series = QCandlestickSeries()
        self.candle_stick_series.setIncreasingColor(Qt.red)
        self.candle_stick_series.setDecreasingColor(Qt.blue)

        self.moving_average_series = QLineSeries()

        self.top_edge_series = QScatterSeries()
        self.bottom_edge_series = QScatterSeries()

        self.chart_view.chart().addSeries(self.candle_stick_series)
        self.chart_view.chart().addSeries(self.moving_average_series)
        self.chart_view.chart().addSeries(self.top_edge_series)
        self.chart_view.chart().addSeries(self.bottom_edge_series)

        self.chart_view.chart().addAxis(self.price_time_axis, Qt.AlignBottom)
        self.chart_view.chart().addAxis(self.price_axis, Qt.AlignLeft)
        self.chart_view.chart().legend().hide()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.set_marker_color()
    
    def set_marker_color(self):
        self.top_edge_series.setPen(Qt.black)
        self.top_edge_series.setBrush(QBrush(Qt.magenta))
        self.bottom_edge_series.setPen(Qt.black)
        self.bottom_edge_series.setBrush(QBrush(Qt.yellow))

    def set_datetime(self, d):
        self.chart_datetime = d
        self.datetime_range = (d.timestamp() * 1000, d.replace(hour=23, minute=59).timestamp() * 1000)
        start_time = QDateTime()
        until_time = QDateTime()
        start_time.setDate(QDate(d.year, d.month, d.day))
        until_time.setDate(QDate(d.year, d.month, d.day))
        start_time.setTime(QTime(9, 0))
        until_time.setTime(QTime(16, 0))
        self.price_time_axis.setRange(start_time, until_time)

    def attach(self):
        self.price_time_axis.setTickCount(7)
        self.candle_stick_series.attachAxis(self.price_time_axis)
        self.candle_stick_series.attachAxis(self.price_axis)
        self.moving_average_series.attachAxis(self.price_time_axis)
        self.moving_average_series.attachAxis(self.price_axis)
        self.top_edge_series.attachAxis(self.price_time_axis)
        self.top_edge_series.attachAxis(self.price_axis)
        self.bottom_edge_series.attachAxis(self.price_time_axis)
        self.bottom_edge_series.attachAxis(self.price_axis)

    def in_datetime_range(self, q):
        return self.datetime_range[0] < q < self.datetime_range[1]

    def clear_series_data(self):
        self.candle_stick_series.clear()
        self.moving_average_series.clear()

    def get_chart_view(self):
        return self.chart_view

    def add_moving_average(self, q, price):
        if self.in_datetime_range(q):
            self.moving_average_series.append(q, price)

    def add_candle_stick(self, q, o, h, l, c):
        if self.in_datetime_range(q):
            self.candle_stick_series.append(QCandlestickSet(o, h, l, c, q))

    def set_price_range(self, price_min, price_max):
        self.price_axis.setRange(price_min, price_max)
        tick_count = int(math.ceil((price_max - price_min) / price_min * 100.))
        self.price_axis.setTickCount(tick_count if tick_count + 1> 2 else 2)
    
    def add_top_edge(self, q, price):
        if self.in_datetime_range(q):
            self.top_edge_series.append(q, price)

    def add_bottom_edge(self, q, price):
        if self.in_datetime_range(q):
            self.bottom_edge_series.append(q, price)

class VolumeFigure:
    def __init__(self, name):
        self.chart_volume_view = QChartView()
        self.chart_volume_view.chart().setLocalizeNumbers(True)
        self.volume_series = QCandlestickSeries()
        
        self.volume_time_axis = QDateTimeAxis()
        self.volume_time_axis.setFormat('h:mm')
        self.volume_axis = QValueAxis()

        self.volume_average_series = QLineSeries()

        self.chart_volume_view.chart().addSeries(self.volume_series)
        self.chart_volume_view.chart().addSeries(self.volume_average_series)

        self.chart_volume_view.chart().addAxis(self.volume_time_axis, Qt.AlignBottom)
        self.chart_volume_view.chart().addAxis(self.volume_axis, Qt.AlignLeft)
        self.chart_volume_view.chart().legend().hide()
        self.chart_volume_view.setRenderHint(QPainter.Antialiasing)

    def in_datetime_range(self, q):
        return self.datetime_range[0] < q < self.datetime_range[1]

    def get_chart_view(self):
        return self.chart_volume_view

    def clear_series_data(self):
        self.volume_series.clear()

    def set_volume_average(self, vol):
        self.volume_average_series.append(self.datetime_range[0], vol)
        self.volume_average_series.append(self.datetime_range[1], vol)

    def set_datetime(self, d):
        self.chart_datetime = d
        self.datetime_range = (d.timestamp() * 1000, d.replace(hour=23, minute=59).timestamp() * 1000)
        start_time = QDateTime()
        until_time = QDateTime()
        start_time.setDate(QDate(d.year, d.month, d.day))
        until_time.setDate(QDate(d.year, d.month, d.day))
        start_time.setTime(QTime(9, 0))
        until_time.setTime(QTime(16, 0))
        self.volume_time_axis.setRange(start_time, until_time)

    def add_volume_data(self, q, volume):
        if self.in_datetime_range(q):
            self.volume_series.append(QCandlestickSet(0, volume, 0, volume, q))

    def attach(self):
        self.volume_time_axis.setTickCount(7)
        self.volume_average_series.attachAxis(self.volume_axis)
        self.volume_average_series.attachAxis(self.volume_time_axis)
        self.volume_series.attachAxis(self.volume_axis)
        self.volume_series.attachAxis(self.volume_time_axis)

    def set_max(self, vol):
        self.volume_axis.setRange(0, vol)


# https://doc.qt.io/qt-5.11/qtcharts-lineandbar-main-cpp.html
class Figure(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        self.yesterday_chart = PriceFigure('yesterday')
        self.today_chart = PriceFigure('today')
        self.yesterday_volume_chart = VolumeFigure('yesterday')
        self.today_volume_chart = VolumeFigure('today')
        self.charts = [self.yesterday_chart, self.today_chart, self.yesterday_volume_chart, self.today_volume_chart]
        self.current_yesterday = None
        self.current_today = None

        self.layout.addWidget(self.yesterday_chart.get_chart_view(), 0, 0)
        self.layout.addWidget(self.today_chart.get_chart_view(), 0, 1)
        self.layout.addWidget(self.yesterday_volume_chart.get_chart_view(), 1, 0)
        self.layout.addWidget(self.today_volume_chart.get_chart_view(), 1, 1)
        self.setLayout(self.layout)

    def clear_chart_data(self):
        for c in self.charts:
            c.clear_series_data()

    def add_moving_average(self, q, price):
        self.yesterday_chart.add_moving_average(q, price)
        self.today_chart.add_moving_average(q, price)

    def add_candle_stick(self, q, o, h, l, c):
        self.yesterday_chart.add_candle_stick(q, o, h, l, c)
        self.today_chart.add_candle_stick(q, o, h, l, c)

    def add_volume_data(self, q, volume):
        self.yesterday_volume_chart.add_volume_data(q, volume)
        self.today_volume_chart.add_volume_data(q, volume)

    def set_volume_max(self, vol):
        self.yesterday_volume_chart.set_max(vol)
        self.today_volume_chart.set_max(vol)

    def set_volume_average(self, vol):
        self.yesterday_volume_chart.set_volume_average(vol)
        self.today_volume_chart.set_volume_average(vol)

    def set_chart_date(self, yesterday, today):
        self.yesterday_chart.set_datetime(yesterday)
        self.yesterday_volume_chart.set_datetime(yesterday)
        self.today_chart.set_datetime(today)
        self.today_volume_chart.set_datetime(today)

    def set_price_range(self, price_min, price_max):
        self.yesterday_chart.set_price_range(price_min, price_max)
        self.today_chart.set_price_range(price_min, price_max)

    def add_bottom_edge(self, q, price):
        self.yesterday_chart.add_bottom_edge(q, price)
        self.today_chart.add_bottom_edge(q, price)

    def add_top_edge(self, q, price):
        self.yesterday_chart.add_top_edge(q, price)
        self.today_chart.add_top_edge(q, price)

    def set_display_data(self, summary):
        self.clear_chart_data()
        print(summary['yesterday'], summary['today'])
        self.set_chart_date(summary['yesterday'], summary['today'])
        self.set_volume_max(max(summary['volume_max'], summary['volume_average']))
        self.set_volume_average(summary['volume_average'])
        self.set_price_range(summary['price_min'], summary['price_max'])
        data = summary['data']

        for d in data:
            self.add_candle_stick(d['time'], d['start_price'], d['highest_price'], d['lowest_price'], d['close_price'])
            self.add_volume_data(d['time'], d['volume'])

        for d in summary['moving_average']:
            self.add_moving_average(d[0], d[1])

        for te in summary['peak_top']:
            print('top', te)
            self.add_top_edge(te[0], te[1])
        
        for be in summary['peak_bottom']:
            print('bottom', te)
            self.add_bottom_edge(be[0], be[1])

        for c in self.charts:
            c.attach()


        
