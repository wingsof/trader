import pytest
from morning.account.cybos_kosdaq_account import CybosKosdaqAccount

# should be connected with CybosPlus
def test_construct():
    cka = CybosKosdaqAccount()
    assert cka.account_balance > 0
    
def test_bid_ask_received():
    cka = CybosKosdaqAccount()

    bid_ask_prices = {
        'target': 'A000010',
        'first_ask_price': 9100,
        'second_ask_price': 9200,
        'third_ask_price': 9300,
        'fourth_ask_price': 9400,
        'fifth_ask_price': 9500,
        'first_bid_price': 8950,
        'second_bid_price': 8900,
        'third_bid_price': 8850,
        'fourth_bid_price': 8800,
        'fifth_bid_price': 8750
    }
    cka.received([bid_ask_prices])
    assert cka.get_ask_price('A000000', 4) == 0
    assert cka.get_ask_price('A000010', 4) == 9500
    assert cka.get_ask_price('A000010', 0) == 9100

def test_transaction():
    cka = CybosKosdaqAccount()
    print(cka.account_balance)
    bid_ask_prices = {
        'target': 'A000010',
        'first_ask_price': 910,
        'second_ask_price': 920,
        'third_ask_price': 930,
        'fourth_ask_price': 940,
        'fifth_ask_price': 950,
        'first_bid_price': 895,
        'second_bid_price': 890,
        'third_bid_price': 885,
        'fourth_bid_price': 880,
        'fifth_bid_price': 875
    }
    cka.received([bid_ask_prices])
    assert cka.transaction({'target': 'A000010', 'result': True, 'value': 9400})[0] == 950
    assert cka.transaction({'target': 'A000010', 'result': False, 'value': 9400})[0] == 875