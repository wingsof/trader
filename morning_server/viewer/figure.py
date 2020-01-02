from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QTimer, QDateTime, QDate, QTime, Qt
from PyQt5.QtChart import QChart, QLineSeries, QCandlestickSeries, QChartView, QDateTimeAxis, QValueAxis, QCandlestickSet, QBarCategoryAxis, QBarSeries, QBarSet
from datetime import time, datetime, timedelta
from utils import time_converter
import numpy as np
import random
import math


# https://doc.qt.io/qt-5.11/qtcharts-lineandbar-main-cpp.html
class Figure(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.chart_view = QChartView()

        #self.category_axis = QBarCategoryAxis()
        #self.category_datetime_border = []

        self.price_time_axis = QDateTimeAxis()
        self.price_time_axis.setFormat('h')

        self.price_axis = QValueAxis()

        self.candle_stick_series = QCandlestickSeries()
        self.candle_stick_series.setCapsWidth(0.1)
        self.candle_stick_series.setBodyWidth(0.9)
        self.candle_stick_series.setIncreasingColor(Qt.red)
        self.candle_stick_series.setDecreasingColor(Qt.blue)

        self.moving_average_series = QLineSeries()

        self.chart_view.chart().addSeries(self.candle_stick_series)
        self.chart_view.chart().addSeries(self.moving_average_series)

        #self.chart_view.chart().addAxis(self.category_axis, Qt.AlignBottom)
        self.chart_view.chart().addAxis(self.price_time_axis, Qt.AlignBottom)
        self.chart_view.chart().addAxis(self.price_axis, Qt.AlignLeft)
        self.chart_view.chart().legend().hide()
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.chart_volume_view = QChartView()
        self.volume_series = QBarSeries()
        self.volume_data_set = QBarSet()

        self.volume_category_axis = QBarCategoryAxis()
        self.volume_axis = QValueAxis()
        self.chart_volume_view.chart().addSeries(self.volume_series)

        self.chart_volume_view.chart().addAxis(self.volume_category_axis, Qt.AlignBottom)
        self.chart_volume_view.chart().addAxis(self.volume_axis, Qt.AlignLeft)
        self.chart_volume_view.chart().legend().hide()
        self.chart_volume_view.setRenderHint(QPainter.Antialiasing)

        self.layout.addWidget(self.chart_view)
        self.layout.addWidget(self.chart_volume_view)
        self.setLayout(self.layout)

    def set_display_data(self, summary):
        self.candle_stick_series.clear()
        self.moving_average_series.clear()
        self.volume_series.clear()

        data = summary['data']

        for i, d in enumerate(data):
            self.moving_average_series.append(d['time'], d['close_price'])
            self.candle_stick_series.append(QCandlestickSet(d['start_price'], d['highest_price'],
                                                            d['lowest_price', d['close_price'] ,d['time']))
            self.volume_data_set.append(d['volume'])

        #categories_x = summary['time_category'].extend(today_summary['time_category'])
        #self.category_axis.setCategories(category_x)
        self.price_time_axis.setRange(summary['yesterday'].replace(hour=9), summary['today'].replace(hour=16))
        self.price_axis.setRange(summary['price_min'], summary['price_max'])
        tick_count = int(math.ceil((summary['price_max'] - summary['price_min']) / summary['price_min'] * 100.))
        self.price_axis.setTickCount(tick_count if tick_count + 1> 2 else 2)

        #self.candle_stick_series.attachAxis(self.category_axis)
        self.candle_stick_series.attachAxis(self.price_time_axis)
        self.candle_stick_series.attachAxis(self.price_axis)

        #self.moving_average_series.attachAxis(self.price_axis)
        self.moving_average_series.attachAxis(self.price_time_axis)
        self.moving_average_series.attachAxis(self.category_axis)

        #self.volume_category_axis.setCategories(category_x)
        self.volume_axis.setRange(summary['volume_min'], summary['volume_max'])
        self.volume_series.append(self.volume_data_set)

        #self.volume_series.attachAxis(self.volume_category_axis)
        self.volume_series.attachAxis(self.price_time_axis)
        self.volume_series.attachAxis(self.volume_axis)
