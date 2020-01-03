from PyQt5.QtWidgets import QGridLayout, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
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

        self.trend_lines = []
        self.short_top_trend_series = QLineSeries()
        self.short_bottom_trend_series = QLineSeries()
        self.long_top_trend_series = QLineSeries()
        self.long_bottom_trend_series = QLineSeries()
        self.trend_lines.append(self.short_top_trend_series)
        self.trend_lines.append(self.short_bottom_trend_series)
        self.trend_lines.append(self.long_top_trend_series)
        self.trend_lines.append(self.long_bottom_trend_series)

        self.chart_view.chart().addSeries(self.candle_stick_series)
        self.chart_view.chart().addSeries(self.moving_average_series)
        self.chart_view.chart().addSeries(self.top_edge_series)
        self.chart_view.chart().addSeries(self.bottom_edge_series)
        self.chart_view.chart().addSeries(self.short_top_trend_series)
        self.chart_view.chart().addSeries(self.long_top_trend_series)
        self.chart_view.chart().addSeries(self.short_bottom_trend_series)
        self.chart_view.chart().addSeries(self.long_bottom_trend_series)

        self.chart_view.chart().addAxis(self.price_time_axis, Qt.AlignBottom)
        self.chart_view.chart().addAxis(self.price_axis, Qt.AlignLeft)
        self.chart_view.chart().legend().hide()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.set_marker_color()
        self.set_trend_line_pen()
    
    def set_trend_line_pen(self):
        brushes = [QBrush(QColor(255, 0, 0, 90)), QBrush(QColor(0, 0, 255, 90)), QBrush(QColor(205, 56, 47, 255)), QBrush(QColor(0, 153, 213, 255))]
        for i, tl in enumerate(self.trend_lines):
            tl.setPen(QPen(brushes[i], 4, Qt.DotLine))

    def set_marker_color(self):
        self.top_edge_series.setPen(Qt.black)
        self.top_edge_series.setBrush(QBrush(QColor(255, 0, 255, 90)))
        self.bottom_edge_series.setPen(Qt.black)
        self.bottom_edge_series.setBrush(QBrush(QColor(0, 255, 255, 90)))

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
        self.short_top_trend_series.attachAxis(self.price_time_axis)
        self.short_top_trend_series.attachAxis(self.price_axis)
        self.long_top_trend_series.attachAxis(self.price_time_axis)
        self.long_top_trend_series.attachAxis(self.price_axis)
        self.short_bottom_trend_series.attachAxis(self.price_time_axis)
        self.short_bottom_trend_series.attachAxis(self.price_axis)
        self.long_bottom_trend_series.attachAxis(self.price_time_axis)
        self.long_bottom_trend_series.attachAxis(self.price_axis)

    def in_datetime_range(self, q):
        return self.datetime_range[0] < q < self.datetime_range[1]

    def clear_series_data(self):
        self.candle_stick_series.clear()
        self.moving_average_series.clear()
        self.top_edge_series.clear()
        self.bottom_edge_series.clear()
        self.short_top_trend_series.clear()
        self.long_top_trend_series.clear()
        self.short_bottom_trend_series.clear()
        self.long_bottom_trend_series.clear()

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

    def add_short_top_trend(self, q, price, draw_horizontal=False):
        if self.in_datetime_range(q):
            if draw_horizontal:
                self.short_top_trend_series.append(q, price)
                if self.name == 'yesterday':
                    self.short_top_trend_series.append(self.datetime_range[1], price)
                else:
                    self.short_top_trend_series.append(self.datetime_range[0], price)
            else:
                self.short_top_trend_series.append(q, price)

    def add_long_top_trend(self, q, price, draw_horizontal=False):
        if self.in_datetime_range(q):
            if draw_horizontal:
                self.long_top_trend_series.append(q, price)
                if self.name == 'yesterday':
                    self.long_top_trend_series.append(self.datetime_range[1], price)
                else:
                    self.long_top_trend_series.append(self.datetime_range[0], price)
            else:
                self.long_top_trend_series.append(q, price)

    def add_short_bottom_trend(self, q, price, draw_horizontal=False):
        if self.in_datetime_range(q):
            if draw_horizontal:
                self.short_bottom_trend_series.append(q, price)
                if self.name == 'yesterday':
                    self.short_bottom_trend_series.append(self.datetime_range[1], price)
                else:
                    self.short_bottom_trend_series.append(self.datetime_range[0], price)
            else:
                self.short_bottom_trend_series.append(q, price)

    def add_long_bottom_trend(self, q, price, draw_horizontal=False):
        if self.in_datetime_range(q):
            if draw_horizontal:
                self.long_bottom_trend_series.append(q, price)
                if self.name == 'yesterday':
                    self.long_bottom_trend_series.append(self.datetime_range[1], price)
                else:
                    self.long_bottom_trend_series.append(self.datetime_range[0], price)
            else:
                self.long_bottom_trend_series.append(q, price)



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
        for c in self.charts:
            c.attach()


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

    def add_short_top_trend(self, q1, price1, q2, price2):
        self.yesterday_chart.add_short_top_trend(q1, price1)
        self.today_chart.add_short_top_trend(q1, price1)
        self.yesterday_chart.add_short_top_trend(q2, price2)
        self.today_chart.add_short_top_trend(q2, price2)

    def add_short_bottom_trend(self, q1, price1, q2, price2):
        self.yesterday_chart.add_short_bottom_trend(q1, price1)
        self.today_chart.add_short_bottom_trend(q1, price1)
        self.yesterday_chart.add_short_bottom_trend(q2, price2)
        self.today_chart.add_short_bottom_trend(q2, price2)

    def add_long_top_trend(self, q1, price1, q2, price2):
        self.yesterday_chart.add_long_top_trend(q1, price1)
        self.today_chart.add_long_top_trend(q1, price1)
        self.yesterday_chart.add_long_top_trend(q2, price2)
        self.today_chart.add_long_top_trend(q2, price2)

    def add_long_bottom_trend(self, q1, price1, q2, price2):
        self.yesterday_chart.add_long_bottom_trend(q1, price1)
        self.today_chart.add_long_bottom_trend(q1, price1)
        self.yesterday_chart.add_long_bottom_trend(q2, price2)
        self.today_chart.add_long_bottom_trend(q2, price2)
    
    def set_display_data(self, summary):
        self.clear_chart_data()
        #print(summary['yesterday'], summary['today'])
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
            #print('top', te)
            self.add_top_edge(te[0], te[1])
        
        for be in summary['peak_bottom']:
            #print('bottom', te)
            self.add_bottom_edge(be[0], be[1])

        st = summary['short_trend']
        self.add_short_top_trend(st[0][0], st[0][1], st[0][2], st[0][3])
        self.add_short_bottom_trend(st[1][0], st[1][1], st[1][2], st[1][3])
        lt = summary['long_trend']
        self.add_long_top_trend(lt[0][0], lt[0][1], lt[0][2], lt[0][3])
        self.add_long_bottom_trend(lt[1][0], lt[1][1], lt[1][2], lt[1][3])
        """    
        if refresh:
            for c in self.charts:
                c.attach()
        """
