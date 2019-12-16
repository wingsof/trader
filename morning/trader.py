from morning.logging import logger
from morning.target_runner import TargetRunner
from PyQt5.QtCore import QThread, pyqtSignal


class Trader(QThread):
    account_msg_arrived = pyqtSignal(object)

    def __init__(self, code, thread_running=False):
        super().__init__()
        self.runner = None
        self.code = code
        self.thread_running = thread_running
        self.account = None
        self.pipelines = []

    def add_pipeline(self, p):
        self.pipelines.append(p)

    def handle_trading(self, msg):
        self.account_msg_arrived.emit(msg)

    def set_account(self, account):
        self.account = account

    def run(self):
        tr = TargetRunner(self.code, self.pipelines, self.handle_trading)
        # streams len should be 1
        while tr.streams[0].received([]) > 0:
            pass


    def start_trading(self):
        if not self.thread_running:
            self.runner = TargetRunner(self.code, self.pipelines, self.handle_trading)
        else:
            self.start()
