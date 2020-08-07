from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QDate, pyqtSlot, pyqtSignal, QEvent
from datetime import datetime
import config


class ActionWidget(QWidget):
    go_next = pyqtSignal()
    go_prev = pyqtSignal()
    play = pyqtSignal()
    stop = pyqtSignal()

    def __init__(self):
        super(ActionWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.time = QLabel('time')
        self.market_type = QLabel('unknown')
        self.go_first = QPushButton('Go Beginning')
        self.prev_b = QPushButton('Prev')
        self.next_b = QPushButton('Next')
        self.play_b = QPushButton('Play')
        self.stop_b = QPushButton('Stop')
        self.next_b.clicked.connect(self.go_next)
        self.prev_b.clicked.connect(self.go_prev)
        self.play_b.clicked.connect(self.play)
        self.stop_b.clicked.connect(self.stop)

        self.layout.addWidget(self.time)
        self.layout.addWidget(self.market_type)
        self.layout.addWidget(self.go_first)
        self.layout.addWidget(self.prev_b)
        self.layout.addWidget(self.next_b)
        self.layout.addWidget(self.play_b)
        self.layout.addWidget(self.stop_b)

        self.setLayout(self.layout)

    @pyqtSlot(int, datetime)
    def infoChanged(self, t, dt):
        #print('infoChanged', t, dt)
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
        elif e.type() == QEvent.KeyPress and e.key() == Qt.Key_Left:
            e.accept()
            self.go_prev.emit()
            return True
        elif e.type() == QEvent.KeyPress and e.key() == Qt.Key_Down:
            e.accept()
            self.play.emit()
            return True
        return QWidget.eventFilter(self, obj, e)
        