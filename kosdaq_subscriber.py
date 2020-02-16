from gevent import monkey; monkey.patch_all()

import os
import sys
import gevent
from clients.vi_follower import main
from morning.back_data import holidays
from datetime import datetime
from multiprocessing import Process


def run_subscriber():
    while True:
        now = datetime.now()
        year, month, day = now.year, now.month, now.day

        is_start_time = datetime(year, month, day, 7) <= now < datetime(year, month, day, 18, 30)
        if not holidays.is_holidays(now.date()) and is_start_time:
            subscribe_process = Process(target=main.start_vi_follower)
            subscribe_process.start()
            subscribe_process.join()

        gevent.sleep(600)    

if __name__ == '__main__':
    run_subscriber()
