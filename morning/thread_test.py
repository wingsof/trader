from pymongo import MongoClient
import pymongo
import time
import sys
import os
from PyQt5.QtCore import QCoreApplication, QTimer, QThread, QObject, QProcess
from PyQt5 import QtCore
from multiprocessing import Process, Queue
from trade_launcher import TradeLauncher


class Worker:
    def __init__(self, q, msg):
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_msg)
        self.queue = q
        self.msg = msg
        self.timer.start(1000)

    def send_msg(self):
        print('PUT MSG', self.msg, os.getpid())
        self.queue.put(self.msg)


def job_function(queue, job_in):
    print('JOB:', job_in)
    app = QCoreApplication(sys.argv)
    w = Worker(queue, job_in)
    app.exec()


class TradeWorker(QObject):

    msg_from_job = QtCore.pyqtSignal(object)

    def __init__(self, job_input):
        print('Create Worker', job_input)
        super(TradeWorker, self).__init__()
        self.job_input = job_input

    def connect_start_signal(self, s):
        s.connect(self._run)

    def _run(self):
        print('Work Thread Started', self.job_input)
        queue = Queue()
        p = Process(target = job_function, args=(queue, self.job_input))
        p.start()
        while True:
            msg = queue.get()
            self.msg_from_job.emit(msg)
            if msg == 'done':
                break


class Trader:
    def __init__(self):
        self.threads = []

    def start(self):
        codes = ['Hello', 'World', 'Welcome']   
        for code in codes:
            runner_thread = QThread()
            worker = TradeWorker(job_input=code)
            self.threads.append((runner_thread, worker))

            worker.msg_from_job.connect(self.handle_msg)
            worker.moveToThread(runner_thread)
            worker.connect_start_signal(runner_thread.started)
            runner_thread.start()
        print('RUN All Threads')

    def handle_msg(self, msg):
        print('MSG to Main Process:', msg, QThread.currentThreadId())


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)

    trader = Trader()

    trader.start()
    app.exec()