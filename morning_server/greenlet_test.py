from greenlet import greenlet
import threading


def test1():
    print('test1', threading.get_ident())
    print(12)
    gr2.switch()
    print(34)


def test2():
    print('test2', threading.get_ident())
    print(56)
    gr1.switch()
    print(78)

gr1 = greenlet(test1)
gr2 = greenlet(test2)
gr1.switch()
