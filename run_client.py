import threading
import time
import _thread

import os
import sys
from datetime import datetime

#sys.stdout = open(os.environ['MORNING_PATH'] + os.sep + 'logs' + os.sep + datetime.now().strftime('%Y%m%d%H%M') + '.log', 'w')
#sys.stderr = sys.stdout

from multiprocessing import Process
from utils.auto import auto
from misc_utils import cybos_com_gen
from morning_server.collectors import shutdown
from morning_server.collectors import request_client
from morning_server import message
from configs import client_info


class ClientRunner(threading.Thread):
    def __init__(self, client_type, client_idx, client_count_info = None):
        threading.Thread.__init__(self)
        self.client_type = client_type
        self.client_index = client_idx
        self.client_count_info = client_count_info

    def run(self):
        while True:
            client_process = Process(target=request_client.run, args=(client_info.get_client_name(), self.client_type, self.client_index, self.client_count_info))
            client_process.start()
            client_process.join()
            time.sleep(30)


if __name__ == '__main__':
    #time.sleep(30) # wait until other startup program is started
    multiprocessing.set_start_method('spawn')
    login_process = Process(target=auto.run)
    login_process.start()
    login_process.join()

    if login_process.exitcode != 0:
        shutdown.go_shutdown(1)
        time.sleep(10)

    time.sleep(10)

    gen_com_process = Process(target=cybos_com_gen.run)
    gen_com_process.start()
    gen_com_process.join()

    time.sleep(10)

    threads = []

    client_count_info = {'trade_count': 0, 'request_count': 0, 'collector_count': 0}
    if client_info.get_client_capability() & message.CAPABILITY_COLLECT_SUBSCRIBE:
        client_count_info['collector_count'] = client_info.get_collector_count()

    if client_info.get_client_capability() & message.CAPABILITY_TRADE:
        client_count_info['trade_count'] = 1
        threads.append(ClientRunner(message.CAPABILITY_TRADE, 0, client_count_info))
    elif client_info.get_client_capability() & message.CAPABILITY_REQUEST_RESPONSE:
        client_count_info['request_count'] = 1
        threads.append(ClientRunner(message.CAPABILITY_REQUEST_RESPONSE, 0, client_count_info))

    if client_info.get_client_capability() & message.CAPABILITY_COLLECT_SUBSCRIBE:
        for i in range(client_info.get_collector_count()):
            if i == 0 and client_count_info['trade_count'] == 0 and client_count_info['request_count'] == 0:
                threads.append(ClientRunner(message.CAPABILITY_COLLECT_SUBSCRIBE, i, client_count_info))
            else:
                threads.append(ClientRunner(message.CAPABILITY_COLLECT_SUBSCRIBE, i))

    for t in threads:
        t.start()
        time.sleep(10)

    for t in threads:
        t.join()
