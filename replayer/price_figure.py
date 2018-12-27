from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QTimer, QDateTime, QDate, QTime, Qt
from PyQt5.QtChart import QChart, QLineSeries, QChartView, QDateTimeAxis, QValueAxis
from datetime import time, datetime, timedelta
import time_converter
import numpy as np
import random


# https://doc.qt.io/qt-5.11/qtcharts-lineandbar-main-cpp.html
class PriceFigure(QWidget):
    def __init__(self):
        super(PriceFigure, self).__init__()
        self.layout = QHBoxLayout()
        self.chart_view = QChartView()
        self.price_series = QLineSeries()
        self.chart_view.chart().addSeries(self.price_series)
        self.chart_view.chart().legend().hide()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.layout.addWidget(self.chart_view)
        self.setLayout(self.layout)
        self.prices = []
        self.volumes = []
        self.graph_time = None
        self.last_timestamp = None

    def set_bound(self, dt, low, high):
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
        axisY.setRange(low, high)
        self.chart_view.chart().setAxisX(axisX, self.price_series)
        self.chart_view.chart().setAxisY(axisY, self.price_series)

    def add_trade(self, timestamp, price, volume, is_buy):
        if self.last_timestamp is None:
            self.set_bound(timestamp, price + price * (-30 / 100.), price + price * (30 / 100.))
            self.last_timestamp = timestamp
            self.graph_time = timestamp
        else:
            if timestamp < self.last_timestamp:
                return
            else:
                self.last_timestamp = timestamp
        
        if timestamp - self.graph_time < timedelta(seconds=60):
            self.prices.append(price)
            self.volumes.append(volume)
        else:
            print('Draw Graph')
            price_mean = np.mean(self.prices)
            self.prices = []
            self.price_series.append(int(timestamp.timestamp() * 1000), price_mean)
            self.graph_time = timestamp
    
    def test_run(self):
        r = random.random()
        if random.random() < 0.5:
            r = -r
        v = random.randint(100, 1000)
        self.current = self.current + self.current * (r / 100.)
        
        self.add_trade(datetime.now() - timedelta(hours=5), self.current, v, True)

    def start_test(self):
        self.set_bound(datetime.now(), 1000, 2000)
        self.timer = QTimer()
        self.timer.timeout.connect(self.test_run)
        self.timer.start(100)
        self.current = 1500

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = QWidget()
    layout = QHBoxLayout()
    fig = PriceFigure()
    layout.addWidget(fig)
    widget.setLayout(layout)
    widget.show()
    fig.start_test()
    app.exec()