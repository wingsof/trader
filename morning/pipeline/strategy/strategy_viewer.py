import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 3))))

from datetime import date

from morning.pipeline.stream.cybos.stock.db.min_tick import MinTick
from morning.pipeline.converter.cybos.stock.day_tick import StockDayTickConverter
from morning.pipeline.chooser.cybos.db.kosdaq_all_chooser import KosdaqAllChooser
from morning.pipeline.strategy.stock.minute_suppressed import MinuteSuppressed
from morning.needle.tick_min_graph_needle import TickMinGraphNeedle
from morning.pipeline.stream.cybos.stock.db.min_excel_tick import MinExcelTick
from morning.needle.tick_excel_needle import TickExcelNeedle

from_date = date(2019, 1, 1)
#mint_tick = MinTick(from_date)
#min_tick.set_target('cybos:A028300')

codes = KosdaqAllChooser().set_date(date(2019, 1, 2)).codes
"""
min_tick = MinExcelTick('sample_data' + os.sep + '20191129_A028300.xlsx')
tmgn = TickMinGraphNeedle(True)
sdtc = StockDayTickConverter()
min_tick.set_output(sdtc)
ms = MinuteSuppressed()

tmgn.tick_connect(ms)
sdtc.set_output(ms)

while min_tick.received(None) > 0:
    pass

min_tick.finalize()
"""