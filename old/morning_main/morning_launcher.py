import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtCore import QCoreApplication, QThread
import signal

from morning.logging import logger


def morning_launcher(allow_interrupt, running_function):
    app = QCoreApplication(sys.argv)
    logger.setup_main_log()
    if allow_interrupt:
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    running_function()

    app.exec()
    logger.exit_main_log()
