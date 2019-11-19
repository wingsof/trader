import pymongo
import sys
from pymongo import MongoClient
from PyQt5.QtCore import QCoreApplication, QObject, pyqtSlot

from morning.trade_launcher import TradeLauncher

class Trader(QObject):
    def __init__(self, is_simulation = False):
        super().__init__()
        self.is_simulation = is_simulation
        self.app = QCoreApplication(sys.argv)

        if self.is_simulation:
            import signal
            signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.trade_launcher = TradeLauncher()
        self.choosers = []
        self.streams = []
        self.executor = None

    def get_db_connection(self):
        try:
            client = MongoClient('mongodb://nnnlife.iptime.org:27017')
            client.server_info()
        except pymongo.errors.ConnectionFailure as e:
            print('Could not connect to server:', e)
            return False
        return True

    def set_chooser(self, seles):
        if type(seles) == list:
            self.choosers.extend(seles)
        else:
            self.choosers.append(seles)

    def set_executor(self, executor):
        self.executor = executor

    def set_stream_pipeline(self, *streams):
        for stream in streams:
            self.streams.append(stream)

    def set_filter_pipeline(self, stream_index, *filt):
        pass

    def ready(self):
        if not self.is_simulation:
            from morning.cybos_api import connection

            conn = connection.Connection()
            if not conn.is_connected():
                print('Network not connected', flush=True)
                return False
            else:
                print('Connect OK')
        
        if not self.get_db_connection():
            print('Cannot connect to Mongo')
            return False
        
        return True

    @pyqtSlot(set)
    def chooser_watcher(self, running_targets):
        for target in running_targets:
            target_information = {'target': target, 
                                  'streams': self.streams,
                                  'converters': [],
                                  'filters':[],
                                  'strategies':[]}
            self.trade_launcher.add_target(target_information)
        self.trade_launcher.launch()


    def run(self):
        for ch in self.choosers:
            ch.code_changed.connect(self.chooser_watcher)
            ch.run()

        self.app.exec()


