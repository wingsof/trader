from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class Chooser(QObject):

    code_changed = pyqtSignal(set)

    def __init__(self):
        super().__init__()

    def start(self):
        pass


if __name__ == '__main__':
    from PyQt5.QtCore import QCoreApplication, QTimer
    import sys
    class Children(Chooser):
        def __init__(self):
            super().__init__()

        def run(self):
            print('emit signal')
            self.code_changed.emit({1,2,3})

    class My(QObject):
        def __init__(self):
            super().__init__()
            self.children = Children()
            self.mylist = set()
            self.children.code_changed.connect(self.my)

        def let_run(self):
            self.children.run()

        @pyqtSlot(set)
        def my(self, msg):
            print('slot')
            self.mylist.update(msg)
            QCoreApplication.quit()
            

    app = QCoreApplication(sys.argv)
    my = My()
    my.let_run()
    assert(my.mylist == {1, 2, 3})
    app.exec()
