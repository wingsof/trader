from PyQt5.QtCore import QCoreApplication, QTimer
import time
import sys
from datetime import datetime

class TimerCheck:
    def __init__(self):
        self.heart_beat = QTimer()
        self.heart_beat.timeout.connect(self.check_time)
        self.int_timer = QTimer()
        self.int_timer.timeout.connect(self.intwork)

    def start(self):
        self.heart_beat.start()
        self.int_timer.start()

    def check_time(self):
        print(datetime.now())

    def intwork(self):
        time.sleep(3)

app = QCoreApplication(sys.argv)
t = TimerCheck()
t.start()
app.exec()
