import threading
import time

import os
import sys
from datetime import datetime

#sys.stdout = open(os.environ['MORNING_PATH'] + os.sep + 'logs' + os.sep + datetime.now().strftime('%Y%m%d%H%M') + '.log', 'w')
#sys.stderr = sys.stdout

from multiprocessing import Process
from utils.auto import auto
from misc_utils import cybos_com_gen
from morning_server.collectors import request_client


def run_request_client():
    while True:
        request_process = Process(target=request_client.run, args=(None,))
        request_process.start()
        request_process.join()
        time.sleep(10)


def run_collector(num):
    while True:
        print('Run collector', num)
        collector_process = Process(target=request_client.run, args=('collector' + str(num),))
        collector_process.start()
        collector_process.join()
        time.sleep(10)


if __name__ == '__main__':
    time.sleep(120)
    login_process = Process(target=auto.run)
    login_process.start()
    login_process.join()
    time.sleep(120)

    gen_com_process = Process(target=cybos_com_gen.run)
    gen_com_process.start()
    gen_com_process.join()

    time.sleep(10)
    
    rclient = Process(target=run_request_client)
    collector1 = Process(target=run_collector, args=(1,))
    collector2 = Process(target=run_collector, args=(2,))
    processes = [rclient, collector1, collector2]
    for p in processes:
        p.start()
        time.sleep(10)

    rclient.join()
    collector1.join()
    collector2.join()
