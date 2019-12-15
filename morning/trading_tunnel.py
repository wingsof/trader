from PyQt5.QtCore import QObject, pyqtSlot, QThread, pyqtSignal
from multiprocessing import Queue

from morning.target_launcher import TargetLauncher
import time


class _QueueReader(QThread):
    msg_from_job = pyqtSignal(object)
    work_done = pyqtSignal()

    def __init__(self, q, count):
        super().__init__()
        self.queue = q
        self.count = count

    def run(self):
        while self.count > 0:
            msg = self.queue.get()
            if msg == 'done':
                self.work_done.emit()
                self.count -= 1
            else:
                self.msg_from_job.emit(msg)


class TradingTunnel(QObject):
    def __init__(self, trader):
        super().__init__()
        self.trader = trader
        self.chooser = None
        self.pipelines = []
        self.workers = []
        self.queue_reader = None
        self.queue = None

    def set_chooser(self, chooser):
        self.chooser = chooser
        self.chooser.selection_changed.connect(self._chooser_selection_changed)

    @pyqtSlot(set)
    def _chooser_selection_changed(self, targets):
        self.trader.runner_count = len(targets)
        self.queue = Queue()
        self.queue_reader = _QueueReader(self.queue, len(targets))
        self.queue_reader.msg_from_job.connect(self.handle_msg)
        self.queue_reader.work_done.connect(self.runner_finished)
        self.queue_reader.start()
        # chooser should deliver targets which not duplicated
        for target in targets:
            worker = TargetLauncher(self.queue, job_input=(target, self.pipelines))
            self.workers.append(worker)
            worker.start_worker()
            #runner_thread.started.connect(self.runner_started)

    def wait_threads(self):
        print('wait_threads--------------')
        self.queue_reader.quit()
        self.queue_reader.wait()
        """
        for thread in self.threads:
            thread.quit()
            thread.wait()
        """

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
