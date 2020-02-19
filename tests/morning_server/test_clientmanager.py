import pytest


from morning_server.clientmanager import ClientManager
from morning_server import message


def test_add_collector():
    c = ClientManager()
    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(1, {'vendor': message.CYBOS}, body)
    assert len(c.get_vendor_collector(message.CYBOS)) == 1

    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    c.add_collector(1, {'vendor': message.KIWOOM}, body)
    assert len(c.get_vendor_collector(message.KIWOOM)) == 1

    assert c.get_available_request_collector() is not None
    assert c.get_available_subscribe_collector() is not None
    assert c.get_available_request_collector(message.KIWOOM) is not None
    assert c.get_available_subscribe_collector(message.KIWOOM) is not None
    assert c.get_available_trade_collector() is None
