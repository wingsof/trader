import pytest

from morning_server import server_util


def test_partial():
    header = {'method': 'day_data'}
    db_data = [{'0': 20191215, '1': 1}, {'0': 20191216, '1': 2}]
    partial = server_util._Partial(header, db_data, 3)
    partial.add_body([{'0': 20191213, '1': 3}, {'0': 20191214, '1': 10}])
    partial.add_body([{'0': 20191217, '1': 3}, {'0': 20191218, '1': 10}])

    assert partial.get_whole_message() == [{'0': 20191213, '1': 3}, {'0': 20191214, '1': 10},
                                            {'0': 20191215, '1': 1}, {'0': 20191216, '1': 2},
                                            {'0': 20191217, '1': 3}, {'0': 20191218, '1': 10}]

    db_data = [{'0': 20191215, '1': 1}, {'0': 20191216, '1': 2}]
    partial = server_util._Partial(header, db_data, 2)
    partial.add_body([])
    partial.add_body([])
    assert partial.get_whole_message() == [{'0': 20191215, '1': 1}, {'0': 20191216, '1': 2}]

    db_data = []
    partial = server_util._Partial(header, db_data, 2)
    partial.add_body([])
    partial.add_body([])
    assert partial.get_whole_message() == []
