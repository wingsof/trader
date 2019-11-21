from PyQt5.QtCore import QCoreApplication, QTimer, QThread, QObject, QProcess, pyqtSignal
from multiprocessing import Process, Queue
from morning.logging import logger
from morning.target_runner import TargetRunner

def _start_target(log_queue, queue, job_info):
    app = QCoreApplication([])
    logger.setup_client(log_queue, job_info[0])
    logger.print('PROCESS START')

    tr = TargetRunner(queue, job_info[0], job_info[1])

    if tr.is_realtime():
        logger.print('Run realtime')
        app.exec()
    else:
        logger.print('Run db')
        tr.db_clock_start()
    logger.print('PROCESS DONE')


class TargetLauncher(QObject):
    msg_from_job = pyqtSignal(object)

    def __init__(self, job_input):
        super().__init__()
        self.job_input = job_input

    def connect_start_signal(self, s):
        s.connect(self._run)

    def _run(self):
        #print('Work Thread Started', self.job_input)
        queue = Queue()
        p = Process(target = _start_target, args=(logger._log_queue, queue, self.job_input))
        p.start()
        while True:
            msg = queue.get()
            self.msg_from_job.emit(msg)
            if msg == 'done':
                break

