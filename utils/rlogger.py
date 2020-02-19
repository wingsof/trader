import logging
import builtins
import sys
import logging.handlers
from datetime import datetime
from configs import client_info
import os
import os.path


def get_log_filename(is_stderr):
    prefix = datetime.now().strftime('%Y%m%d')
    if is_stderr:
        ext = '_err.log'
    else:
        ext = '.log'

    path = ''
    try:
        path = os.environ['MORNING_PATH'] + os.sep + 'logs' + os.sep
    except KeyError:
        print('NO MORNING_PATH SYSTEM ENVIRONMENT VARIABLE') 
    start_index = 0
    filename = path + prefix + ext

    while os.path.exists(filename):
        start_index += 1
        filename = path + prefix + '_' + str(start_index) + ext
    return filename


def except_hook(exc_type, exc_value, traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, traceback)
        return

    _logger.error('Logging an uncaught exception', exc_info=(exc_type, exc_value, traceback))


def _setup_log(use_console_out=True):
    logg = logging.getLogger(client_info.get_client_name())
    logg.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logg.addHandler(stream_handler)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    socket_handler = logging.handlers.SocketHandler(client_info.get_server_ip(),
                        logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    socket_handler.setFormatter(formatter)
    logg.addHandler(socket_handler)
    return logg


def info(msg, *args, **kwargs):
    _logger.info(msg, *args, *kwargs)


def warning(msg, *args, **kwargs):
    _logger.warning(msg, *args, *kwargs)


def error(msg, *args, **kwargs):
    _logger.error(msg, *args, *kwargs)


def critical(msg, *args, **kwargs):
    _logger.critical(msg, *args, *kwargs)


def log(msg, *args, **kwargs):
    _logger.critical(msg, *args, *kwargs)


_logger = _setup_log()
sys.excepthook = except_hook
