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
from morning_server.collectors import shutdown


if __name__ == '__main__':
    ready_filename = os.environ['MORNING_PATH'] + os.sep + 'READY'

    try:
        os.remove(ready_filename)
    except:
        print('READY file not exist')

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

    open(ready_filename, 'w+')
