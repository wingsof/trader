import logging
from multiprocessing import Process, Queue
import time
import logger

def setup_log(queue):
    logg = logging.getLogger('morning_main')
    logg.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logg.addHandler(stream_handler)

    file_handler = logging.FileHandler('log_morning_main.log')
    logg.addHandler(file_handler)
    while True:
        msg = queue.get()
        logg.info(msg)

        if msg == 'done':
            break


def start_process(queue):
    logger.log_queue = queue
    i = 0
    while True:
        time.sleep(1)
        logger.print('new_proces, hello world', i)
        i += 1


if __name__ == '__main__':
    log_queue = Queue()
    p = Process(target = setup_log, args=(log_queue,))
    p.start()

    p2 = Process(target = start_process, args=(log_queue,))
    p2.start()

    logger.log_queue = log_queue

    while True:
        time.sleep(1)
        logger.print('main process, hello world')
    p.wait()
    p2.wait()
    # create queue and setup log system in new process
    # create process and deliver log queue
    # send message from main and new process to test whether queue process is working
    # -> OK
    # wrapping logging class
