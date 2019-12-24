import pytest


def pytest_configure(config):
    from morning.trade_record import _called_from_test
    _called_from_test=True
