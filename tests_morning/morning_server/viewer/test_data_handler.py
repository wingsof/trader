import pytest
from morning_server.viewer import data_handler

def test_data_handler():
    datahandler = data_handler.DataHandler()
    sample_data = [
        {'0': 20191227, 'time': 910,  'close_price': 1000, 'start_price': 900, 'highest_price': 1100, 'lowest_price': 900, 'volume': 100},
        {'0': 20191227, 'time': 912,  'close_price': 1100, 'start_price': 1000, 'highest_price': 1200, 'lowest_price': 1000, 'volume': 100},
        {'0': 20191227, 'time': 914,  'close_price': 1200, 'start_price': 1000, 'highest_price': 1300, 'lowest_price': 900, 'volume': 100},
        {'0': 20191227, 'time': 916,  'close_price': 1100, 'start_price': 900, 'highest_price': 1100, 'lowest_price': 900, 'volume': 100},
        {'0': 20191227, 'time': 919,  'close_price': 1000, 'start_price': 900, 'highest_price': 1100, 'lowest_price': 800, 'volume': 100},
        {'0': 20191227, 'time': 911,  'close_price': 900, 'start_price': 900, 'highest_price': 1100, 'lowest_price': 900, 'volume': 100},
    ]
    result = datahandler.create_summary_data(sample_data)
    assert result['price_max'] == 1300
    assert len(result['data']) == 2
    assert result['price_min'] == 800
    assert result['data'][1]['close_price'] == 900
