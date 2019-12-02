import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 3))))

from datetime import date

from morning.pipeline.stream.cybos.stock.db.min_tick import MinTick
from morning.pipeline.converter.cybos.stock.day_tick import StockDayTickConverter
from morning.pipeline.strategy.stock.minute_suppressed import MinuteSuppressed
from morning.needle.tick_min_graph_needle import TickMinGraphNeedle


from_date = date(2019, 11, 29)
mt = MinTick(from_date)
mt.set_target('cybos:A028300')
tmgn = TickMinGraphNeedle(True)

sdtc = StockDayTickConverter()
mt.set_output(sdtc)
ms = MinuteSuppressed()

tmgn.tick_connect(ms)
sdtc.set_output(ms)

while mt.received(None) > 0:
    pass

mt.finalize()
