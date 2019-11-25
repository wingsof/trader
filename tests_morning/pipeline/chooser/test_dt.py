
import pytest
from morning.pipeline.converter import dt

def test_cybos_stock_tick():
    a = {'0': 'A005930', '1': 'Samsung'}
    new_a = dt.cybos_stock_tick_convert(a)
    assert dt.stock_tick[dt.CybosStockTick.CODE] in new_a.keys()
    assert dt.stock_tick[dt.CybosStockTick.COMPANY_NAME] in  new_a.keys()

def test_cybos_ba_stock_tick():
    a = {'0': 'A005930', '23': 123456}
    new_b = dt.cybos_stock_ba_tick_convert(a)
    assert dt.stock_ba_tick[dt.CybosStockBidAskTick.CODE] in new_b.keys()
    assert dt.stock_ba_tick[dt.CybosStockBidAskTick.TOTAL_ASK_REMAIN] in new_b.keys()
