import logging
from multiprocessing import Queue, Process


_log_queue = None
_log_prefix = ''

def _get_msg_to_string(msg_tuple):
    msg = ''
    for i, m in enumerate(msg_tuple):
        if i == 0:
            msg = str(m)
        else:
            msg = msg + ' ' + str(m)
    return msg


def _put_msg(loglevel, msg):
    global _log_queue
    if _log_queue:
        _log_queue.put_nowait((loglevel, '[' + _log_prefix + ']\t' + _get_msg_to_string(msg)))
    else:
        print(msg)


def print(*args):
    _put_msg(logging.INFO, args)


def warning(*args):
    _put_msg(logging.WARNING, args)


def error(*args):
    _put_msg(logging.ERROR, args)


def setup_client(queue, prefix):
    global _log_queue, _log_prefix
    _log_queue = queue
    _log_prefix = prefix


def _setup_log(queue):
    logg = logging.getLogger('morning')
    logg.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logg.addHandler(stream_handler)

    file_handler = logging.FileHandler('log_morning.log')
    file_handler.setFormatter(formatter)
    logg.addHandler(file_handler)
    while True:
        msg = queue.get()
        logg.log(msg[0], msg[1])

        if msg[0] == -1:
            break


def exit_main_log():
    global _log_queue
    _log_queue.put_nowait([-1, -1])


def setup_main_log():
    global _log_queue, _log_prefix
    _log_queue = Queue()
    p = Process(target = _setup_log, args=(_log_queue,))
    p.start()
    _log_prefix = 'main'
    return _log_queue