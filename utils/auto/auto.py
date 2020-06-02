from utils.auto import windep
import time
from utils.auto import winkey
import random
import datetime
from datetime import timedelta
import sys
import win32clipboard

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..' + os.sep + '..')))
from configs import client_info


def send_word(word):
    for c in word:
        if c == '^':
            winkey.send_special_key(winkey.VK_CODE['6'])
        elif c == '@':
            winkey.send_special_key(winkey.VK_CODE['2'])
        else:
            winkey.send_key(winkey.VK_CODE[c])

        print('input', c)
        time.sleep(2)


def run():
    win = windep.WinDep()
    state = 0
    notice_wait_time = None
    while True:
        time.sleep(1)

        if state == 0 and win.keyboard_security_found():
            time.sleep(5)
            winkey.send_key(winkey.VK_CODE['enter'])
            state = 1
        elif state == 1:
            if win.starter_found():
                state = 2
                time.sleep(10)
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(client_info.get_client_password())
                win32clipboard.CloseClipboard()
                winkey.send_paste_key()
                time.sleep(5)
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(client_info.get_client_certificate_password())
                win32clipboard.CloseClipboard()
                winkey.send_paste_key()
                time.sleep(1)
                winkey.send_key(winkey.VK_CODE['enter'])
        elif state == 2:
            if notice_wait_time is None:
                notice_wait_time = datetime.datetime.now()

            if win.popup_notice_found():
                state = 3
            elif datetime.datetime.now() - notice_wait_time > timedelta(seconds=60):
                sys.exit(1)
        elif state == 3:
            sys.exit(0)

if __name__ == '__main__':
    run()
