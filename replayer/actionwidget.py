from PyQt5.QtWidgets import *


class ActionWidget(QWidget):
    def __init__(self):
        super(ActionWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.prev = QPushButton('Prev')
        self.next = QPushButton('Next')

        self.layout.addWidget(self.prev)
        self.layout.addWidget(self.next)

        self.setLayout(self.layout)