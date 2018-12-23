from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate, pyqtSlot, pyqtSignal, QEvent
from datetime import datetime
import config


class ActionWidget(QWidget):
    go_next = pyqtSignal()

    def __init__(self):
        super(ActionWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.time = QLabel('time')
        self.market_type = QLabel('unknown')
        self.go_first = QPushButton('Go Beginning')
        self.prev = QPushButton('Prev')
        self.next = QPushButton('Next')
        self.next.clicked.connect(self.go_next)

        self.layout.addWidget(self.time)
        self.layout.addWidget(self.market_type)
        self.layout.addWidget(self.go_first)
        self.layout.addWidget(self.prev)
        self.layout.addWidget(self.next)

        self.setLayout(self.layout)

    @pyqtSlot(int, datetime)
    def infoChanged(self, t, dt):
        print('infoChanged', t, dt)
        self.time.setText(dt.strftime('%Y-%m-%d %X'))
        if t == config.BEFORE_MARKET:
            self.market_type.setText('BEFORE')
        elif t == config.IN_MARKET:
            self.market_type.setText('IN')
        elif t == config.AFTER_MARKET:
            self.market_type.setText('AFTER')

    def eventFilter(self, obj, e):
        if e.type() == QEvent.KeyPress and e.key() == Qt.Key_Right:
            e.accept()
            self.go_next.emit()
            return True
        return QWidget.eventFilter(self, obj, e)
        