from morning.pipeline.converter import dt
from morning.logging import logger


class StockTickConverter:
    def __init__(self):
        self.next_elements = None

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
        if self.next_elements is not None:
            converted_datas = []
            for data in datas:
                converted_datas.append(dt.cybos_stock_tick_convert(data))
            self.next_elements.received(converted_datas)



"""
0: code
1: name - company_name
2: 전일대비 - yesterday_diff
3: 시간 - time
4: 시가 - start_price
5: 고가 - highest_price
6: 저가 - lowest_price
7: 매도호가 - ask_price
8: 매수호가 - bid_price
9: 누적거래량 - cum_volume
10: 누적거래대금(만원), - cum_amount
13: 현재가 또는 예상체결가(19번 구분 플래그에 따라 달라짐) - current_price
14: 현재가 또는 체결상태('1' 매수, '2' 매도) - buy_or_sell
15: 누적매도체결수량(체결가) - cum_sell_volume
16: 누적매수체결수량(체결가) - cum_buy_volume
17: 순간체결 수량 - volume
18: 시간 - time_with_sec
19: 예상체결가구분('1' 동시호가시간 '2' 장중) - market_type_exp
20: 장구분('1' 장전예상체결 '2' 장중 '3' 장전시간외 '4' 장후시간외 '5' 장후예상체결) - market_type
21: 장전시간외 거래량 - out_time_volume
22: 대비부호 ('1' 상한, '2' 상승..)
23: LP 보유량
24: LP... 
26: 체결상태('1' 매수 '2' 매도) 
27: 누적매도체결수량(호가)
28: 누적매수체결수량(호가)
"""
