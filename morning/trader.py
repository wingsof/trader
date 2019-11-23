from PyQt5.QtCore import QCoreApplication, QObject, QTimer, pyqtSlot
import sys
import signal


class Trader(QObject):
    def __init__(self, realtime = True):
        # TODO: remove below line
        super().__init__()
        self.realtime = realtime
        self.account = None

        if not self.realtime:
            signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.app = QCoreApplication(sys.argv)
        self.trade_tunnels = []

    def ready(self):
        return True

    def add_tunnel(self, tunnel):
        self.trade_tunnels.append(tunnel)

    def handle_trading(self, msg):
        if self.account:
            self.account.transaction(msg)

    def set_account(self, account):
        self.account = account

    @pyqtSlot()
    def _run(self):
        for tt in self.trade_tunnels:
            tt.run()

    def run(self):
        # if not use app.exec(), no way to receive message from QThread signal
        QTimer.singleShot(1000, self._run)
        self.app.exec()
