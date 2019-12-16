from morning.logging import logger
from morning.target_runner import TargetRunner
from PyQt5.QtCore import QThread


class Trader(QThread):
    def __init__(self, code, thread_running=True):
        self.runner = None
        self.code = code
        self.thread_running = thread_running
        self.account = None
        self.pipelines = []

    def add_pipeline(self, p):
        self.pipelines.append(p)

    def handle_trading(self, msg):
        logger.print('Handle Trading:', msg)
        if self.account:
            self.account.transaction(msg)

    def set_account(self, account):
        self.account = account

    def run(self):
        TargetRunner(self.code, self.pipelines, self.handle_trading)
        pass

    def start_trading(self):
        if not self.thread_running:
            self.runner = TargetRunner(self.code, self.pipelines, self.handle_trading)
        else:
            self.start()
