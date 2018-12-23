import sys
from PyQt5.QtWidgets import QApplication
import mainwidget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = mainwidget.MainWidget()
    app.installEventFilter(w.action)
    w.show()
    app.exec()