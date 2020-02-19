import pytest

from configs import client_info
client_info.TEST_MODE = True

from morning_server.clientmanager import ClientManager
from morning_server import message
from tests.morning_server import mock_server_util

def test_add_collector():
    c = ClientManager()
    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(1, {'vendor': message.CYBOS}, body)
    assert len(c.get_vendor_collector(message.CYBOS)) == 1

    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(2, {'vendor': message.KIWOOM}, body)
    assert len(c.get_vendor_collector(message.KIWOOM)) == 1

    assert c.get_available_request_collector() is not None
    assert c.get_available_subscribe_collector() is not None
    assert c.get_available_request_collector(message.KIWOOM) is not None
    assert c.get_available_subscribe_collector(message.KIWOOM) is not None


def test_connect_to_subscribe():
    c = ClientManager()
    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(1, {'vendor': message.CYBOS}, body)
    c.connect_to_subscribe('A00001', 100, {}, {})
    collector = c.get_available_subscribe_collector()
    assert 'A00001' in collector.subscribe_code


def test_disconnect_to_subscribe():
    c = ClientManager()
    c.disconnect_to_subscribe('A00001', 100, {}, {})
    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(1, {'vendor': message.CYBOS}, body)
    c.connect_to_subscribe('A00001', 100, {}, {})
    c.disconnect_to_subscribe('A00001', 100, {}, {})
    collector = c.get_available_subscribe_collector()
    assert 'A00001' not in collector.subscribe_code
    assert 'A00001' not in c.code_subscribe_info
    c.connect_to_subscribe('A00001', 100, {}, {})
    c.connect_to_subscribe('A00002', 101, {}, {})
    collector = c.get_available_subscribe_collector()
    assert len(collector.subscribe_code) == 2
    assert 'A00001' in c.code_subscribe_info
    assert 'A00002' in c.code_subscribe_info


def test_handle_block_request_response():
    c = ClientManager()
    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(1, {'vendor': message.CYBOS}, body)
    c.handle_block_request(200, {'_id': '12345'}, {})

    collector = c.find_request_by_id('12345')
    assert collector is not None
    assert collector.request['pending']
    c.handle_block_response(200, {'_id': '12345'}, {})
    assert not collector.request['pending']
    assert c.find_request_by_id('12345') is None


def test_handle_trade_block_request_response():
    c = ClientManager()
    body = {'capability': message.CAPABILITY_TRADE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(1, {'vendor': message.CYBOS}, body)
    collector = c.get_available_trade_collector()
    c.handle_trade_block_request(200, {'_id': '12345'}, {})
    assert collector.request['pending']
    c.handle_trade_block_response(200, {'_id': '12345'}, {})
    c.handle_trade_block_response(200, {'_id': '12345'}, {})
    assert not collector.request['pending']

def test_connect_to_trade_subscribe():
    c = ClientManager()
    body = {'capability': message.CAPABILITY_TRADE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.connect_to_trade_subscribe(100, message.CYBOS)
    # not yet collector is added
    assert 100 not in c.trade_subscribe_sockets[message.CYBOS]
    c.add_collector(1, {'vendor': message.CYBOS}, body)
    c.connect_to_trade_subscribe(100, message.CYBOS)
    assert 100 in c.trade_subscribe_sockets[message.CYBOS]
    c.disconnect_to_trade_subscribe(100)
    assert 100 not in c.trade_subscribe_sockets[message.CYBOS]

def test_broadcast_trade_data():
    c = ClientManager()
    body = {'capability': message.CAPABILITY_TRADE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(1, {'vendor': message.CYBOS}, body)
    mock_server_util.last_msg.clear()
    c.connect_to_trade_subscribe(100, message.CYBOS)
    c.connect_to_trade_subscribe(200, message.CYBOS)
    c.broadcast_trade_data({}, {})
    assert mock_server_util.last_msg[-2][0] == 100
    assert mock_server_util.last_msg[-1][0] == 200
    mock_server_util.last_msg.clear()

def test_disconnect_to_trade_subscribe():
    c = ClientManager()
    body = {'capability': message.CAPABILITY_TRADE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(7, {'vendor': message.CYBOS}, body)

    mock_server_util.last_msg.clear()
    c.disconnect_to_trade_subscribe(100, message.CYBOS)
    assert len(mock_server_util.last_msg) == 0
    c.connect_to_trade_subscribe(100, message.CYBOS)
    assert 100 in c.trade_subscribe_sockets[message.CYBOS]
    c.disconnect_to_trade_subscribe(100, message.CYBOS)
    assert len(mock_server_util.last_msg) == 1
    assert mock_server_util.last_msg[0][0] == 7
    assert mock_server_util.last_msg[0][1]['method'] == message.STOP_TRADE_DATA

def test_socket_disconnect_collector():
    c = ClientManager()
    body = {'capability': message.CAPABILITY_TRADE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(7, {'vendor': message.CYBOS}, body)

    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(11, {'vendor': message.CYBOS}, body)

    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(13, {'vendor': message.CYBOS}, body)
    c.connect_to_subscribe('A00001', 100, {}, {})
    c.connect_to_subscribe('A00001' + message.BIDASK_SUFFIX, 101, {}, {})
    c.connect_to_subscribe('A00001' + message.SUBJECT_SUFFIX, 102, {}, {})
    for collector in c.collectors:
        assert len(collector.subscribe_code) == 1

    assert 'A00001' in c.code_subscribe_info
    assert 'A00001' + message.BIDASK_SUFFIX in c.code_subscribe_info
    assert 'A00001' + message.SUBJECT_SUFFIX  in c.code_subscribe_info
    assert len(c.code_subscribe_info) == 3
    c.handle_disconnect(11)
    assert len(c.collectors) == 2
    assert len(c.code_subscribe_info) == 2


def test_socket_disconnect_client():
    c = ClientManager()
    body = {'capability': message.CAPABILITY_TRADE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(7, {'vendor': message.CYBOS}, body)

    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(11, {'vendor': message.CYBOS}, body)

    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(13, {'vendor': message.CYBOS}, body)
    c.connect_to_subscribe('A00001', 100, {}, {})
    c.connect_to_subscribe('A00001' + message.BIDASK_SUFFIX, 101, {}, {})
    c.connect_to_subscribe('A00001' + message.SUBJECT_SUFFIX, 102, {}, {})
    mock_server_util.last_msg.clear()
    c.handle_disconnect(102)
    assert 'A00001' in c.code_subscribe_info
    assert 'A00001' + message.BIDASK_SUFFIX in c.code_subscribe_info
    assert 'A00001' + message.SUBJECT_SUFFIX not in c.code_subscribe_info
    assert mock_server_util.last_msg[-1][1]['method'] == message.STOP_SUBJECT_DATA

    c.handle_disconnect(100)
    assert mock_server_util.last_msg[-1][1]['method'] == message.STOP_STOCK_DATA
    assert len(c.collectors) == 3
