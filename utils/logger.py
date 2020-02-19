import logging
import builtins
import sys, os
import logging.handlers
from datetime import datetime
import os.path
from utils import morning_filename as mf


def except_hook(exc_type, exc_value, traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, traceback)
        return

    _logger.error('Logging an uncaught exception', exc_info=(exc_type, exc_value, traceback))


def _setup_log():
    sys.stdout = open(mf.get_log_filename(False), 'w+')
    sys.stderr = open(mf.get_log_filename(True), 'w+')
    logg = logging.getLogger('morning')
    logg.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logg.addHandler(stream_handler)

    """
    filename = 'logs' + os.sep + 'morning_server.log'
    try:
        filename = os.environ['MORNING_PATH'] + os.sep + filename
        if not os.path.exists(os.environ['MORNING_PATH'] + os.sep + 'logs'):
            os.mkdir(os.environ['MORNING_PATH'] + os.sep + 'logs')
    except KeyError:
        print('NO MORNING_PATH SYSTEM ENVIRONMENT VARIABLE') 

    file_handler = logging.handlers.RotatingFileHandler(filename, maxBytes=2**20, backupCount=1000)
    file_handler.setFormatter(formatter)
    logg.addHandler(file_handler)
    """
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
