from PyQt5.QtCore import QCoreApplication, QObject, QTimer, pyqtSlot, QEventLoop
import sys
import signal
from morning.logging import logger


class Trader(QObject):
    def __init__(self, realtime = True):
        # TODO: remove below line
        super().__init__()
        #logger.setup_main_log()

        self.realtime = realtime
        self.account = None
        self.runner_count = -1


        
        self.app = QEventLoop()
        #self.app = QCoreApplication(sys.argv)
        self.trade_tunnels = []

    def ready(self):
        return True

    def add_tunnel(self, tunnel):
        self.trade_tunnels.append(tunnel)

    def handle_trading(self, msg):
        if self.account:
            self.account.transaction(msg)

    def increment_runner(self):
        if self.runner_count == -1:
            self.runner_count = 1
        else:
            self.runner_count += 1
        logger.print('RUNNER(+)', self.runner_count)

    def decrement_runner(self):
        if self.runner_count > 0:
            self.runner_count -= 1
        else:
            logger.print('Runner finished before started')
        logger.print('RUNNER(-)', self.runner_count)

        if not self.realtime and self.runner_count is 0:
            self.app.quit()

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