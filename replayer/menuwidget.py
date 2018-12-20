from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDialog, QCalendarWidget
from PyQt5.QtCore import QDate, pyqtSlot, pyqtSignal
from datetime import datetime


class DatePick(QDialog):
    date_selected = pyqtSignal('QDate')

    def __init__(self):
        super(DatePick, self).__init__()
        self.setModal(True)

        self.layout = QHBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.activated.connect(self.date_selected)
        self.layout.addWidget(self.calendar)
        self.setLayout(self.layout)


class MenuWidget(QWidget):
    info_changed = pyqtSignal(str, datetime)

    def __init__(self):
        super(MenuWidget, self).__init__()
        self.now = QDate.currentDate()
        self.init_ui()

    def update_date(self):
        self.date_input.setText(self.now.toString('yyyy/M/d'))

    @pyqtSlot('QDate')
    def date_changed(self, date):
        self.now = date
        self.update_date()

    @pyqtSlot()
    def pick_date(self):
        pick = DatePick()
        pick.date_selected.connect(self.date_changed)
        pick.date_selected.connect(pick.accept)
        pick.exec()

    @pyqtSlot()
    def set_next_day(self):
        self.now = self.now.addDays(1)
        self.update_date()

    @pyqtSlot()
    def send_info(self):
        code = str(self.code_input.text())
        dt = datetime(self.now.year(), self.now.month(), self.now.day() - 1)
        self.info_changed.emit(code, dt)

    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.code_label = QLabel('Code')
        self.code_input = QLineEdit('A035420')

        self.date_label = QPushButton('Date')
        self.date_label.clicked.connect(self.pick_date)
        self.date_input = QLabel(self.now.toString('yyyy/M/d'))

        self.search_button = QPushButton('Search')
        self.search_button.clicked.connect(self.send_info)

        self.next_day = QPushButton('Next day')
        self.next_day.clicked.connect(self.set_next_day)

        self.layout.addWidget(self.code_label)
        self.layout.addWidget(self.code_input)
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.date_input)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.next_day)
        self.setLayout(self.layout)