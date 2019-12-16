from morning.logging import logger
from morning.target_runner import TargetRunner


class Trader(QObject):
    def __init__(self, code):
        super().__init__()
		self.runner = None
		self.code = code
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
		self.runner = TargetRunner(code, self.pipelines, self.handle_trading)
