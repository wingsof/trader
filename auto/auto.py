import windep
import time
import winkey
import random
import datetime
import sys

def send_word(word):
    for c in word:
        if c == '^':
            print('special key')
            winkey.send_special_key(winkey.VK_CODE['6'])
        else:
            winkey.send_key(winkey.VK_CODE[c])

        print('input', c)
        time.sleep(1)


if __name__ == '__main__':
    win = windep.WinDep()
    state = 0
    time.sleep(10)
    while True:
        time.sleep(1)

        if state == 0 and win.keyboard_security_found():
            time.sleep(5)
            winkey.send_key(winkey.VK_CODE['enter'])
            state = 1
            print('Keyboard good')
        elif state == 1:
            if win.starter_found():
                state = 2
                time.sleep(5)
                send_word('dyddn007')              
                send_word('gkdtkd6^tkfwk')
                winkey.send_key(winkey.VK_CODE['enter'])
        elif state == 2:
            time.sleep(10)
            sys.exit(0)
