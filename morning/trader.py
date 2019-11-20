from PyQt5.QtCore import QCoreApplication, QObject, QTimer, pyqtSlot
import sys
import signal


class Trader(QObject):
    def __init__(self):
        # TODO: remove below line
        super().__init__()
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.app = QCoreApplication(sys.argv)
        self.trade_tunnels = []

    def ready(self):
        return True

    def add_tunnel(self, tunnel):
        self.trade_tunnels.append(tunnel)

    def set_account(self, account):
        pass

    @pyqtSlot()
    def _run(self):
        for tt in self.trade_tunnels:
            tt.run()

    def run(self):
        QTimer.singleShot(1000, self._run)
        self.app.exec()
