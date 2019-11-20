from PyQt5.QtCore import QCoreApplication, QTimer, QThread, QObject, QProcess, pyqtSignal
from multiprocessing import Process, Queue


def _start_target(queue, job_info):
    app = QCoreApplication([])
    print('NEW Proces')
    app.exec()



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
        p = Process(target = _start_target, args=(queue, self.job_input))
        p.start()
        while True:
            msg = queue.get()
            self.msg_from_job.emit(msg)
            if msg == 'done':
                break

