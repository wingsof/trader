import time
import pytest

from multiprocessing import Process
from morning.logging import logger


def start_process(queue):
    logger.setup_client(queue, 'client')
    i = 0
    while True:
        time.sleep(1)
        logger.warning('new_proces, hello world', i)
        i += 1


def test_logging():
    q = logger.setup_main_log()

    p2 = Process(target = start_process, args=(q,))
    p2.start()

    while True:
        time.sleep(1)
        logger.warning('main process, hello world')
    
    p2.wait()


if __name__ == '__main__':
    test_logging()