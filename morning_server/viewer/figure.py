from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QTimer, QDateTime, QDate, QTime, Qt
from PyQt5.QtChart import QChart, QLineSeries, QCandlestickSeries, QChartView, QDateTimeAxis, QValueAxis, QCandlestickSet, QBarCategoryAxis
from datetime import time, datetime, timedelta
from utils import time_converter
import numpy as np
import random


# https://doc.qt.io/qt-5.11/qtcharts-lineandbar-main-cpp.html
class Figure(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.chart_view = QChartView()

        self.category_axis = QBarCategoryAxis()
        self.price_axis = QValueAxis()

        self.candle_stick_series = QCandlestickSeries()
        self.candle_stick_series.setCapsWidth(0.1)
        self.candle_stick_series.setBodyWidth(0.9)
        self.candle_stick_series.setIncreasingColor(Qt.red)
        self.candle_stick_series.setDecreasingColor(Qt.blue)

        self.moving_average_series = QLineSeries()

        self.chart_view.chart().addSeries(self.candle_stick_series)
        self.chart_view.chart().addSeries(self.moving_average_series)

        self.chart_view.chart().addAxis(self.category_axis, Qt.AlignBottom)
        self.chart_view.chart().addAxis(self.price_axis, Qt.AlignLeft)
        self.chart_view.chart().legend().hide()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.layout.addWidget(self.chart_view)
        self.setLayout(self.layout)

    def set_data(self, yesterday, target_date, yesterday_min, today_min):
        print('set_data', len(yesterday_min))
        yesterday_min = yesterday_min[:30]
        self.candle_stick_series.clear()
        self.moving_average_series.clear()

        high = 0
        low = 0

        for i, ym in enumerate(yesterday_min):
            open = ym['start_price']
            close = ym['close_price']
            highest = ym['highest_price']
            lowest = ym['lowest_price']
            if high == 0:
                high = highest
            elif high < highest:
                high = highest

            if low == 0:
                low = lowest
            elif low > lowest:
                low = lowest
            t = time_converter.intdate_to_datetime(ym['0'])
            t = t.replace(hour=int(ym['time'] / 100), minute=int(ym['time'] % 100))
            self.category_axis.append(t.strftime('%H:%M'))
            print(open, highest, lowest, close)
            self.moving_average_series.append(i, close)
            self.candle_stick_series.append(QCandlestickSet(open, highest, lowest, close))
        self.price_axis.setRange(low, high)
        
        self.candle_stick_series.attachAxis(self.category_axis)
        self.candle_stick_series.attachAxis(self.price_axis)

        self.moving_average_series.attachAxis(self.price_axis)
        self.moving_average_series.attachAxis(self.category_axis)
        #self.chart_view.chart().createDefaultAxes()
        

        #self.chart_view.chart().setAxisX(self.category_axis, self.moving_average_series)
        #self.chart_view.chart().setAxisY(self.price_axis, self.candle_stick_series)
        #self.chart_view.chart().setAxisY(self.price_axis, self.moving_average_series)
