from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QTimer, QDateTime, QDate, QTime, Qt
from PyQt5.QtChart import QChart, QLineSeries, QChartView, QDateTimeAxis, QValueAxis
from datetime import time, datetime, timedelta
import time_converter
from numpy import random
import numpy as np


class SpeedFigure(QWidget):
    def __init__(self):
        super(SpeedFigure, self).__init__()
        self.layout = QVBoxLayout()
        self.chart_view = []
        self.line_series = [[],[]]
        self.y_axis = []
        self.default_max_y_value = 3000
        self.colors = [Qt.red, Qt.blue, Qt.green, Qt.magenta]
        for i in range(2):
            cv = QChartView()
            for j in range(4):
                ls = QLineSeries()
                p = ls.pen()
                p.setColor(self.colors[j])
                ls.setPen(p)
                self.line_series[i].append(ls)
                cv.chart().addSeries(ls)
    
            cv.chart().legend().hide()
            cv.chart().layout().setContentsMargins(0, 0, 0, 0);

            cv.setRenderHint(QPainter.Antialiasing)
            self.chart_view.append(cv)
            self.layout.addWidget(cv)

        self.last_timestamp = None

        self.setLayout(self.layout)
    
    def start_test(self):
        self.set_date(datetime.now())
        self.timer = QTimer()
        self.timer.timeout.connect(self.test_run)
        self.timer.start(100)
        self.current = 0

    def test_run(self):
        arr = random.randint(3500, size=8)
        if self.current % 2 == 0:
            self.add_trade_speed(datetime.now() - timedelta(hours=6), arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], arr[6], arr[7])
        else:
            self.add_spread_speed(datetime.now() - timedelta(hours=6), arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], arr[6], arr[7])
        self.current += 1

    def set_date(self, dt):
        for i in range(2):
            axisX = QDateTimeAxis()
            axisX.setFormat('h:mm')
            start_time = QDateTime()
            finish_time = QDateTime()
            start_time.setDate(QDate(dt.year, dt.month, dt.day))
            start_time.setTime(QTime(9, 0))
            finish_time.setDate(QDate(dt.year, dt.month, dt.day))
            finish_time.setTime(QTime(15, 30))
            axisX.setRange(start_time, finish_time)
            axisY = QValueAxis()
            axisY.setRange(0, self.default_max_y_value)
            self.y_axis.append(axisY)
            self.chart_view[i].chart().setAxisX(axisX)
            self.chart_view[i].chart().setAxisY(axisY)
            for j in range(4):
                self.line_series[i][j].attachAxis(axisX)
                self.line_series[i][j].attachAxis(axisY)

    def add_trade_speed(self, timestamp, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30):
        if self.last_timestamp is None:
            self.last_timestamp = timestamp
        else:
            if timestamp < self.last_timestamp:
                return
        period = ((bid_10, ask_10), (bid_30, ask_30))

        for i in range(2):
            for j in range(2):
                if period[i][j] > self.default_max_y_value:
                    self.default_max_y_value = period[i][j]
                    for y in self.y_axis:
                        y.setRange(0, self.default_max_y_value)
                    break

        for i in range(2):
            for j in range(2):
                self.line_series[i][j].append(int(timestamp.timestamp() * 1000), period[i][j])

    def add_spread_speed(self, timestamp, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30):
        if self.last_timestamp is None:
            self.last_timestamp = timestamp
        else:
            if timestamp < self.last_timestamp:
                return

        period = ((bid_10, ask_10), (bid_30, ask_30))

        for i in range(2):
            for j in range(2):
                if period[i][j] > self.default_max_y_value:
                    self.default_max_y_value = period[i][j]
                    for y in self.y_axis:
                        y.setRange(0, self.default_max_y_value)
                    break
        
        for i in range(2):
            for j in range(2, 4):
                self.line_series[i][j].append(int(timestamp.timestamp() * 1000), period[i][j - 2])

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    import matplotlib
    #matplotlib.use('Qt5Agg')

    app = QApplication(sys.argv)
    widget = QWidget()
    layout = QHBoxLayout()
    fig = SpeedFigure()
    layout.addWidget(fig)
    widget.setLayout(layout)
    widget.show()
    fig.start_test()
    app.exec()