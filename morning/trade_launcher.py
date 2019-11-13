from pymongo import MongoClient
import pymongo
import time
import sys
from PyQt5.QtCore import QCoreApplication, QTimer, QThread, QObject, QProcess
from PyQt5 import QtCore
from multiprocessing import Process, Queue
import os
from observe_realtime_code import ObserveRealtimeCode


def start_observe_data(queue, code):
    app = QCoreApplication(sys.argv)
    o = ObserveRealtimeCode(queue, code)
    o.start_observe()
    app.exec()


class TradeWorker(QObject):

    msg_from_job = QtCore.pyqtSignal(object)

    def __init__(self, job_input):
        #print('Create Worker', job_input)
        super(TradeWorker, self).__init__()
        self.job_input = job_input

    def connect_start_signal(self, s):
        s.connect(self._run)

    def _run(self):
        print('Work Thread Started', self.job_input)
        queue = Queue()
        p = Process(target = start_observe_data, args=(queue, self.job_input))
        p.start()
        while True:
            msg = queue.get()
            self.msg_from_job.emit(msg)
            if msg == 'done':
                break


class TraderLauncher:
    def __init__(self, codes):
        self.codes = codes
        self.workers = []

    def launch(self):
        for code in self.codes:
            runner_thread = QThread()
            worker = TradeWorker(job_input=code)

            worker.msg_from_job.connect(self.handle_msg)
            worker.moveToThread(runner_thread)

            self.workers.append((code, runner_thread, worker))

            worker.connect_start_signal(runner_thread.started)
            runner_thread.start()
        print('RUN All Threads')

    def set_account_info(self, account_num, account_type, balance):
        self.account_num = account_num
        self.account_type = account_type
        self.balance = balance

    def handle_msg(self, msg):
        print('MSG to Main Process:', msg, QThread.currentThreadId())


