
_log_queue = None

def print(*args):
    global log_queue
    msg = ''
    for i, m in enumerate(args):
        if i == 0:
            msg = str(m)
        else:
            msg = msg + ' ' + str(m)

    if log_queue:
        log_queue.put_nowait(msg)


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


def setup_main_log():
    global _log_queue
    _log_queue = Queue()
    p = Process(target = setup_log, args=(log_queue,))
    p.start()

