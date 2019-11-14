import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
import pymongo
import time
from PyQt5.QtCore import QCoreApplication, QTimer, QThread
from multiprocessing import Process, Queue

from morning.chooser import kosdaq_current_bull_codes
from morning.account import cybos_account, fake_account

is_simulation = True

if is_simulation:
    from dbapi import connection
    from dbapi import config
else:
    from winapi import connection
    from winapi import config


class Trader:
    def __init__(self, is_simulation = False):
        self.app = QCoreApplication(sys.argv)

    def get_db_connection(self):
        try:
            client = MongoClient(config.MONGO_SERVER)
            client.server_info()
        except pymongo.errors.ConnectionFailure as e:
            print('Could not connect to server:', e)
            return False
        return True

    def set_selector(self, sele):
        pass

    def set_executor(self, executor):
        pass

    def set_stream_pipeline(self, *streams):
        # Use clock connect between streams when simulation is on
        pass

    def set_filter_pipeline(self, stream_index, *filt):
        pass

    def ready(self):
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

    def run(self):
        # start selector
        self.app.exec()


