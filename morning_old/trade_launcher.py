from pymongo import MongoClient
import pymongo
import time
import sys
from PyQt5.QtCore import QCoreApplication, QTimer, QThread, QObject, QProcess
from PyQt5 import QtCore
from multiprocessing import Process, Queue
import os
#from observe_realtime_code import ObserveRealtimeCode

from morning.pipeline.pipeline import Pipeline

def start_observe_data(queue, elements_info):
    app = QCoreApplication([])
    print('JOB INPUT', elements_info)

    pipeline = Pipeline(elements_info, queue) 
    pipeline.start()
    #o = ObserveRealtimeCode(queue, code)
    #o.start_observe()

    app.exec()


class TradeWorker(QObject):

    msg_from_job = QtCore.pyqtSignal(object)

    def __init__(self, job_input):
        super().__init__()
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


class TradeLauncher:
    def __init__(self):
        self.targets = []
        self.workers = []

    def add_target(self, target):
        self.targets.append(target)
        print('ADD TARGET', len(self.targets))

    def launch(self):
        print('RUN All Threads', len(self.targets))

        for target in self.targets:
            print('Create Thread')
            runner_thread = QThread()
            worker = TradeWorker(job_input=target)

            worker.msg_from_job.connect(self.handle_msg)
            worker.moveToThread(runner_thread)

            self.workers.append((target, runner_thread, worker))

            worker.connect_start_signal(runner_thread.started)
            runner_thread.start()
        self.targets.clear()
        # TODO: before 9:00 AM, check Cp7043 for today surge codes

    def set_account_info(self, account_num, account_type, balance):
        self.account_num = account_num
        self.account_type = account_type
        self.balance = balance

    def handle_msg(self, msg):
        print('MSG to Main Process:', msg, QThread.currentThreadId())


