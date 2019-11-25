import time
import pytest

from multiprocessing import Process
from morning.logging import logger


def start_process(queue):
    logger.setup_client(queue, 'client')
    i = 0
    time.sleep(1)
    logger.warning('new_proces, hello world', i)
    time.sleep(1)


def test_logging():
    q = logger.setup_main_log()

    p2 = Process(target = start_process, args=(q,))
    p2.start()

    time.sleep(1)
    logger.warning('main process, hello world')
    time.sleep(3)
    logger._log_queue.put_nowait([-1, -1])
    

