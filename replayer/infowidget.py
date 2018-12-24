from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt5.QtCore import pyqtSlot

class InfoWidget(QWidget):
    def __init__(self):
        super(InfoWidget, self).__init__()
        self.speed_labels = [
            '1 MIN BID',
            '1 MIN ASK',
            '10 MIN BID',
            '10 MIN ASK',
            '20 MIN BID',
            '20 MIN ASK',
            '30 MIN BID',
            '30 MIN ASK'
        ]
        self.speed_label_widget = []
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()
        self.speed_layout = QGridLayout()
        for i, label in enumerate(self.speed_labels):
            self.speed_layout.addWidget(QLabel(label), i, 0)
            l = QLabel('0')
            self.speed_layout.addWidget(l, i, 1)
            self.speed_label_widget.append(l)

        self.layout.addLayout(self.speed_layout, 0, 1)
        self.setLayout(self.layout)

    @pyqtSlot(float, float, float, float, float, float, float, float)
    def speedChanged(self, bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30):
        l = [bid_1, ask_1, bid_10, ask_10, bid_20, ask_20, bid_30, ask_30]
        for i, num in enumerate(l):
            self.speed_label_widget[i].setText('{0:0.1f}'.format(num))