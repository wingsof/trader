import windep
import time
import winkey
import random
import datetime
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
    time.sleep(10)
    while True:
        time.sleep(1)

        if state == 0 and win.keyboard_security_found():
            time.sleep(5)
            winkey.send_key(winkey.VK_CODE['enter'])
            state = 1
        elif state == 1:
            if win.starter_found():
                state = 2
                time.sleep(20)
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
            time.sleep(30)
            sys.exit(0)

if __name__ == '__main__':
    run()
