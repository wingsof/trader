import multiprocessing

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from multiprocessing import Process

from stock_service.plugins import today_bull
from utils import trade_logger


_LOGGER = trade_logger.get_logger('PLUGIN STARTER')

plugins = [
    today_bull.plugin_run,
]

def start_plugins():
    
    processes = []
    
    _LOGGER.info('START PLUGINS count: %d', len(plugins))
    for p in plugins:
        plugin = Process(target=p)
        processes.append(plugin)


    for p in processes:
        p.start()

    for p in processes:
        p.join()


if __name__ == '__main__':
    start_plugins()
