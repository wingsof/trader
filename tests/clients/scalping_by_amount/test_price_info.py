import pytest

from clients.scalping_by_amount import price_info


def test_price_slot():
    l = price_info.create_slots(9000, 9500, 9100, False)
    first_vi_index = -1
    for i in range(len(l[0])):
        if l[0][i] == 10000: # actual 10% -> 10010
            first_vi_index = i
            break
    assert l[1][first_vi_index] == price_info.VI_MARK

    second_vi_index = -1
    for i in range(len(l[0])):
        if l[0][i] == 10900: # actual 20% -> 10920
            second_vi_index = i
            break
    assert l[1][second_vi_index] == price_info.VI_MARK

    l = price_info.create_slots(6000, 6050, 6030, False)
    first_vi_index = -1
    for i in range(len(l[0])):
        if l[0][i] == 6630: # actual 10% -> 6633
            first_vi_index = i
            break
    assert l[1][first_vi_index] == price_info.VI_MARK

    second_vi_index = -1
    for i in range(len(l[0])):
        if l[0][i] == 7230: # actual 20% -> 7236
            second_vi_index = i
            break
    assert l[1][second_vi_index] == price_info.VI_MARK


def test_order_sheet():
    price_slots = [6060, 6070, 6080, 6090, 6100, 6110, 6120, 6130, 6140, 6150]
    slots = price_info.create_order_sheet(price_slots, 1)
    assert len(slots) == 1
    assert slots[0][0] == 6060
    assert slots[0][1] == 1

    slots = price_info.create_order_sheet(price_slots, 10)
    for i, slot in enumerate(slots):
        assert slot[0] == price_slots[i]
        assert slot[1] == 1

    slots = price_info.create_order_sheet(price_slots, 11)
    for i, slot in enumerate(slots):
        assert slot[0] == price_slots[i]
        if i == 9:
            slot[1] == 2
        else:
            assert slot[1] == 1
    
    slots = price_info.create_order_sheet(price_slots, 17)
    assert len(slots) == 10
    assert slots[0][1] == 1
    assert slots[1][1] == 2  # 1.7 + 0.7 = 2.4
    assert slots[2][1] == 2  # 1.7 + 0.4 = 2.1
    assert slots[3][1] == 1  # 1.7 + 0.1 = 1.8
    assert slots[4][1] == 2  # 1.7 + 0.8 = 2.5
    assert slots[5][1] == 2  # 1.7 + 0.5 = 2.2
    assert slots[6][1] == 1  # 1.7 + 0.2 = 1.9
    assert slots[7][1] == 2  # 1.7 + 0.9 = 2.6
    assert slots[8][1] == 2  # 1.7 + 0.6 = 2.3
    assert slots[9][1] == 2