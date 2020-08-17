import logging
import builtins
import sys, os
import logging.handlers
from datetime import datetime
import os.path


_logger = None
log_count = 0

def except_hook(exc_type, exc_value, traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, traceback)
        return

    _logger.error('Logging an uncaught exception', exc_info=(exc_type, exc_value, traceback))


def _setup_log():
    logg = logging.getLogger('TRADER')
    logg.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(module)s][%(process)d][%(funcName)s][%(lineno)d] %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logg.addHandler(stream_handler)

    prefix = datetime.now().strftime('%Y%m%d%H%M')
    filename = 'logs' + os.sep + 'trader_' + prefix + '.log'
    try:
        filename = os.environ['MORNING_PATH'] + os.sep + filename
        if not os.path.exists(os.environ['MORNING_PATH'] + os.sep + 'logs'):
            os.mkdir(os.environ['MORNING_PATH'] + os.sep + 'logs')
    except KeyError:
        print('NO MORNING_PATH SYSTEM ENVIRONMENT VARIABLE') 

    file_handler = logging.handlers.RotatingFileHandler(filename, maxBytes=2**20, backupCount=1000)
    file_handler.setFormatter(formatter)
    logg.addHandler(file_handler)
    return logg


def info(msg, *args, **kwargs):
    _logger.info(str(datetime.now()) + '\t' + msg, *args, *kwargs)


def warning(msg, *args, **kwargs):
    _logger.warning(str(datetime.now()) + '\t' + msg, *args, *kwargs)


def error(msg, *args, **kwargs):
    _logger.error(str(datetime.now()) + '\t' + msg, *args, *kwargs)


def critical(msg, *args, **kwargs):
    _logger.critical(str(datetime.now()) + '\t' + msg, *args, *kwargs)


def log(msg, *args, **kwargs):
    _logger.log(str(datetime.now()) + '\t' + msg, *args, *kwargs)


def get_logger():
    global _logger, log_count
    if _logger is None:
        log_count += 1
        _logger = _setup_log()
        sys.excepthook = except_hook
    return _logger
