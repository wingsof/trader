import pytest
import pandas as pd
from morning.pipeline.strategy.stock.start_with_up import StartWithUp


def test_add_next_min():
    swu = StartWithUp(3)

    t1 = 90100
    t2 = 95900
    t3 = 90159
    assert swu._add_next_min(t1) == 90200
    assert swu._add_next_min(t2) == 100000 
    assert swu._add_next_min(t3) == 90259


def test_check_dataframe():
    #df = pd.read_excel('tests_morning/pipeline/strategy/stock/three_up.xlsx')
    swu = StartWithUp(3)
    datas = [{'time_with_sec': 90100, 'current_price': 100},
            {'time_with_sec': 90130, 'current_price': 200},
            {'time_with_sec': 90201, 'current_price': 300},
            {'time_with_sec': 90241, 'current_price': 400},
            {'time_with_sec': 90303, 'current_price': 500},
            {'time_with_sec': 90353, 'current_price': 600},
            {'time_with_sec': 90405, 'current_price': 500}]
    df = pd.DataFrame(datas)
    assert swu.check_dataframe(df)

    datas = [{'time_with_sec': 90100, 'current_price': 100},
            {'time_with_sec': 90130, 'current_price': 200},
            {'time_with_sec': 90201, 'current_price': 100},
            {'time_with_sec': 90241, 'current_price': 200},
            {'time_with_sec': 90303, 'current_price': 100},
            {'time_with_sec': 90353, 'current_price': 200},
            {'time_with_sec': 90405, 'current_price': 0}]

    df = pd.DataFrame(datas)
    assert swu.check_dataframe(df)

    datas = [{'time_with_sec': 90100, 'current_price': 100},
            {'time_with_sec': 90130, 'current_price': 50},
            {'time_with_sec': 90201, 'current_price': 100},
            {'time_with_sec': 90241, 'current_price': 200},
            {'time_with_sec': 90303, 'current_price': 100},
            {'time_with_sec': 90353, 'current_price': 200},
            {'time_with_sec': 90405, 'current_price': 0}]

    df = pd.DataFrame(datas)
    assert not swu.check_dataframe(df)

    datas = [{'time_with_sec': 90100, 'current_price': 100},
            {'time_with_sec': 90130, 'current_price': 200},
            {'time_with_sec': 90201, 'current_price': 200},
            {'time_with_sec': 90241, 'current_price': 100},
            {'time_with_sec': 90303, 'current_price': 100},
            {'time_with_sec': 90353, 'current_price': 200},
            {'time_with_sec': 90405, 'current_price': 0}]
    df = pd.DataFrame(datas)
    assert not swu.check_dataframe(df)


def test_received():
    class Receiver:
        def __init__(self):
            self.result = None
            self.is_get = False

        def received(self, datas):
            self.is_get = True
            self.result = datas

    swu = StartWithUp(3)
    rcv = Receiver()
    swu.set_output(rcv)

    datas = [{'time_with_sec': 90100, 'current_price': 100},
            {'time_with_sec': 90130, 'current_price': 50},
            {'time_with_sec': 90201, 'current_price': 100},
            {'time_with_sec': 90241, 'current_price': 200},
            {'time_with_sec': 90303, 'current_price': 100},
            {'time_with_sec': 90353, 'current_price': 200},
            {'time_with_sec': 90405, 'current_price': 0}]

    swu.received(datas[:-1])
    swu.received(datas[-1:])
    assert not rcv.is_get

    swu = StartWithUp(3)
    rcv = Receiver()
    swu.set_output(rcv)

    datas = [{'time_with_sec': 90100, 'current_price': 100},
            {'time_with_sec': 90130, 'current_price': 200},
            {'time_with_sec': 90201, 'current_price': 100},
            {'time_with_sec': 90241, 'current_price': 200},
            {'time_with_sec': 90303, 'current_price': 100},
            {'time_with_sec': 90353, 'current_price': 200},
            {'time_with_sec': 90405, 'current_price': 0}]
    swu.received(datas[:-1])
    swu.received(datas[-1:])
    assert len(rcv.result) == 1
    #assert rcv.result[0]['value'] == 'True'
