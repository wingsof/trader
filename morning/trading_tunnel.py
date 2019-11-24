from PyQt5.QtCore import QObject, pyqtSlot, QThread
from morning.target_launcher import TargetLauncher


class TradingTunnel(QObject):
    def __init__(self, trader):
        super().__init__()
        self.trader = trader
        self.chooser = None
        self.pipelines = []
        self.targets = []

    def set_chooser(self, chooser):
        self.chooser = chooser
        self.chooser.selection_changed.connect(self._chooser_selection_changed)

    @pyqtSlot(set)
    def _chooser_selection_changed(self, targets):
        # chooser should deliver targets which not duplicated
        for target in targets:
            runner_thread = QThread()
            worker = TargetLauncher(job_input=(target, self.pipelines))
            worker.msg_from_job.connect(self.handle_msg)

            worker.work_done.connect(self.runner_finished)
            runner_thread.started.connect(self.runner_started)

            worker.moveToThread(runner_thread)
            self.targets.append((target, runner_thread, worker))
            worker.connect_start_signal(runner_thread.started)
            runner_thread.start()

    @pyqtSlot()
    def runner_started(self):
        self.trader.increment_runner()

    @pyqtSlot()
    def runner_finished(self):
        self.trader.decrement_runner()

    def add_pipeline(self, p):
        self.pipelines.append(p)

    def run(self):
        if self.chooser:
            self.chooser.start()

    def handle_msg(self, msg):
        self.trader.handle_trading(msg)
        print('MSG to Main Process:', msg)
