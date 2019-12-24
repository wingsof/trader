from PyQt5.QtCore import QCoreApplication, QTimer, QThread, QObject, QProcess, pyqtSignal, QMutex, QMutexLocker
from multiprocessing import Process
from morning.logging import logger
from morning.target_runner import TargetRunner

def _start_target(queue, job_info):
    app = QCoreApplication([])
    logger.setup_client(log_queue, job_info[0])
    logger.print('PROCESS START', job_info[0])

    tr = TargetRunner(queue, job_info[0], job_info[1])

    if tr.is_realtime():
        app.exec()
    else:
        tr.db_clock_start()

    logger.print('PROCESS DONE', job_info[0])
    queue.put('done')
    queue.close()


class TargetLauncher(QObject):
    def __init__(self, q, job_input):
        super().__init__()
        self.job_input = job_input
        self.queue = q
        self.p = None

    def start_worker(self):
        self.p = Process(target = _start_target, args=(logger._log_queue, self.queue, self.job_input))
        self.p.start()
        """
        while True:
            msg = queue.get()
            if msg == 'done':
                logger.print('OK, quit')
                self.work_done.emit()
                break
            self.msg_from_job.emit(msg)
        """
