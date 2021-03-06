import time
import win32ui, win32gui, win32con, win32api
from PIL import Image
import datetime

hwnd = None
title = ''


def enumHandler(h, lParam):
    global hwnd
    global title
    if win32gui.IsWindowVisible(h):
        window_title = win32gui.GetWindowText(h).strip()
        if len(window_title) > 0:
            print('title', window_title)
            if title in window_title:
                hwnd = h
                print("Found window handle: {}".format(h))


class WinDep:
    def setting(self):
        win32gui.EnumWindows(enumHandler, None)
        l, t, r, b = win32gui.GetWindowRect(hwnd)
        self.window_width = r - l
        self.window_height = b - t
        self.capture_time = datetime.datetime.now()
        #print("Window Size: %dx%d" % (self.window_width, self.window_height))
        win32gui.SetForegroundWindow(hwnd)
        win32gui.ShowWindow(hwnd, 1)

    def __init__(self):
        pass

    def print_windows(self):
        win32gui.EnumWindows(enumHandler, None)

    def starter_found(self):
        if self.window_found('Starter'):
            return True
        
    def keyboard_security_found(self):
        if self.window_found('CREON', 408, 221):
            return True
            
    def popup_notice_found(self):
        if not self.window_found('Starter'):
            return True
        return False

    def window_found(self, name, width=-1, height=-1):
        global hwnd
        global title

        title = name
        win32gui.EnumWindows(enumHandler, None)
        if hwnd is not None:
            """
            l, t, r, b = win32gui.GetWindowRect(hwnd)
            window_width = r - l
            window_height = b - t
            if (width == -1 and height == -1) or (window_width == width and window_height == height):
            """
            try:
                win32gui.SetForegroundWindow(hwnd)
                win32gui.ShowWindow(hwnd, 1)
                hwnd = None
                title = None
                return True
            except:
                print('exception occured')
                return False
        hwnd = None
        title = None
        return False
