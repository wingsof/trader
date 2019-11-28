from morning.pipeline.converter import dt


class StockBidAskTickConverter:
    def __init__(self):
        self.next_elements = None

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def finalize(self):
        if self.next_elements:
            self.next_elements.finalize()

    def received(self, datas):
        if self.next_elements is not None:
            converted_datas = []
            for data in datas:
                converted_datas.append(dt.cybos_stock_ba_tick_convert(data))
            self.next_elements.received(converted_datas)


"""
0 - (string) 종목코드 - code
1 - (long) 시간 - time
2 - (long) 거래량 - volume
3 - (long) 1차매도호가 - first_ask_price
4 - (long) 1차매수호가 - first_bid_price
5 - (long) 1차매도잔량 - first_ask_remain_volume
6 - (long) 1차매수잔량 - first_bid_remain_volume
7 - (long) 2차매도호가 - 
8 - (long) 2차매수호가
9 - (long) 2차매도잔량
10 - (long) 2차매수잔량
11 - (long) 3차매도호가
12 - (long) 3차매수호가
13 - (long) 3차매도잔량
14 - (long) 3차매수잔량
15 - (long) 4차매도호가
16 - (long) 4차매수호가
17 - (long) 4차매도잔량
18 - (long) 4차매수잔량
19 - (long) 5차매도호가
20 - (long) 5차매수호가
21 - (long) 5차매도잔량
22 - (long) 5차매수잔량
23 - (long) 총매도잔량
24 - (long) 총매수잔량
25 - (long) 시간외총매도잔량
26 - (long) 시간외총매수잔량
27 - (long) 6차매도호가
28 - (long) 6차매수호가
29 - (long) 6차매도잔량
30 - (long) 6차매수잔량
31 - (long) 7차매도호가
32 - (long) 7차매수호가
33 - (long) 7차매도잔량
34 - (long) 7차매수잔량
35 - (long) 8차매도호가
36 - (long) 8차매수호가
37 - (long) 8차매도잔량
38 - (long) 8차매수잔량
39 - (long) 9차매도호가
40 - (long) 9차매수호가
41 - (long) 9차매도잔량
42 - (long) 9차매수잔량
43 - (long) 10차매도호가
44 - (long) 10차매수호가
45 - (long) 10차매도잔량
46 - (long) 10차매도잔량
47 - (long) 1차LP매도잔량
48 - (long) 1차LP매수잔량
49 - (long) 2차LP매도잔량
50 - (long) 2차LP매수잔량
51 - (long) 3차LP매도잔량
52 - (long) 3차LP매수잔량
53 - (long) 4차LP매도잔량
54 - (long) 4차LP매수잔량
55 - (long) 5차LP매도잔량
56 - (long) 5차LP매수잔량
57 - (long) 6차LP매도잔량
58 - (long) 6차LP매수잔량
59 - (long) 7차LP매도잔량
60 - (long) 7차LP매수잔량
61 - (long) 8차LP매도잔량
62 - (long) 8차LP매수잔량
63 - (long) 9차LP매도잔량
64 - (long) 9차LP매수잔량
65 - (long) 10차LP매도잔량
66 - (long) 10차LP매수잔량
67 - (long) LP매도잔량 10차합
68 - (long) LP매수잔량10차합

"""
