from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from datetime import time, datetime
import matplotlib.dates as mdates
import time_converter


class SpeedFigure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = [fig.add_subplot(411)]
        self.axes.append(fig.add_subplot(412))
        self.axes.append(fig.add_subplot(413))
        self.axes.append(fig.add_subplot(414))
        self.last_timestamp = None
        
        super(SpeedFigure, self).__init__(fig)
    
    def set_date(self, dt):
        start_time = datetime(dt.year, dt.month, dt.day, 8, 0)
        end_time = datetime(dt.year, dt.month, dt.day, 16, 0)
        xfmt = mdates.DateFormatter('%H:%M')
        for ax in self.axes:
            ax.cla()
            ax.set_xlim([start_time, end_time])
            ax.xaxis.set_major_formatter(xfmt)
        self.draw()

    def add_trade_speed(self, timestamp, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30):
        if self.last_timestamp is None:
            self.last_timestamp = timestamp
        else:
            if timestamp < self.last_timestamp:
                return
        l = [1, 10, 20, 30]
        period = ((bid_1, ask_1), (bid_10, ask_10), (bid_20, ask_20), (bid_30, ask_30))
        
        for i, minute in enumerate(l):
            self.axes[i].plot(timestamp, period[i][0], 'r-')
            self.axes[i].plot(timestamp, period[i][1], 'b-')
        self.draw()

    def add_spread_speed(self, timestamp, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30):
        if self.last_timestamp is None:
            self.last_timestamp = timestamp
        else:
            if timestamp < self.last_timestamp:
                return
        l = [1, 10, 20, 30]
        period = ((bid_1, ask_1), (bid_10, ask_10), (bid_20, ask_20), (bid_30, ask_30))
        
        for i, minute in enumerate(l):
            self.axes[i].plot(timestamp, period[i][0], 'g--')
            self.axes[i].plot(timestamp, period[i][1], 'c--')
        self.draw()

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
    app.exec()