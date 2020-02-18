from gevent import monkey; monkey.patch_all()

from pymongo import MongoClient
from gevent.server import StreamServer
from datetime import datetime
import threading
import stream_readwriter
import time
import gevent


from utils import logger_server, logger
import os
import sys
import gevent
from clients.vi_follower import main
from morning.back_data import holidays
from clients.vi_data_validation import data_validation
from datetime import datetime
from multiprocessing import Process
from morning_server import server
from configs import time_info


vbox_on = False


def run_subscriber():
    while True:
        now = datetime.now()
        year, month, day = now.year, now.month, now.day

        is_start_time = datetime(year, month, day, time_info.SUBSCRIBER_START_TIME['hour']) <= now < datetime(year, month, day, time_info.SUBSCRIBER_FINISH_TIME['hour'], time_info.SUBSCRIBER_FINISH_TIME['minute'])
        if not holidays.is_holidays(now.date()) and is_start_time:
            subscribe_process = Process(target=main.start_vi_follower)
            subscribe_process.start()
            subscribe_process.join()
            gevent.sleep(600)
            validate_process = Process(target=data_validation.start_validation)
            validate_process.start()
            validate_process.join()

        gevent.sleep(600)
 

def run_server(is_vbox_on):
    while True:
        server_process = Process(target=morning_server.start_server, args=(is_vbox_on,))
        server_process.start()
        server_process.join()


if len(sys.argv) > 1 and sys.argv[1] == 'vbox':
    vbox_on = True

log_server = Process(target=logger_server.start_log_server)
log_server.start()

gevent.spawn(run_server, vbox_on)
gevent.spawn(run_subscriber)
log_server.join()
