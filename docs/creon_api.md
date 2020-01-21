stockcur

0: code
1: name
2: 전일대비
3: 시간
4: 시가
5: 고가
6: 저가
7: 매도호가
8: 매수호가
9: 누적거래량
10: 누적거래대금(만원), 
13: 현재가 또는 예상체결가(19번 구분 플래그에 따라 달라짐)
14: 현재가 또는 체결상태('1' 매수, '2' 매도)
15: 누적매도체결수량(체결가)
16: 누적매수체결수량(체결가)
17: 순간체결 수량
18: 시간
19: 예상체결가구분('1' 동시호가시간 '2' 장중)
20: 장구분('1' 장전예상체결 '2' 장중 '3' 장전시간외 '4' 장후시간외 '5' 장후예상체결)
21: 장전시간외 거래량
22: 대비부호 ('1' 상한, '2' 상승..)
23: LP 보유량
24: LP... 
26: 체결상태('1' 매수 '2' 매도) 
27: 누적매도체결수량(호가)
28: 누적매수체결수량(호가)

stockchart

0: 날짜(ulong)
1:시간(long) - hhmm
2:시가(long or float)
3:고가(long or float)
4:저가(long or float)
5:종가(long or float)
8(6):거래량(ulong or ulonglong)주) 정밀도만원단위
9(7):거래대금(ulonglong)
10(8):누적체결매도수량(ulong or ulonglong) -호가비교방식누적체결매도수량
11(9):누적체결매수수량(ulong or ulonglong) -호가비교방식누적체결매수수량
 (주) 10, 11 필드는분,틱요청일때만제공
16(10):외국인현보유수량(ulong)
17(11):외국인현보유비율(float)
20(12):기관순매수(long)
21(13):기관누적순매수(long)


stockjpbid
0 - (string) 종목코드
1 - (long) 시간
2 - (long) 거래량
3 - (long) 1차매도호가
4 - (long) 1차매수호가
5 - (long) 1차매도잔량
6 - (long) 1차매수잔량
7 - (long) 2차매도호가
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

7240
0 - (ulong) 일자
1 - (long) 종가
2 - (double) 전일대비
3 - (long) 대비율
4 - (long) 거래량
5 - (long) 공매도량
6 - (long) 대차
7 - (long) 상환
8 - (long) 대차잔고증감
9 - (long) 대차잔고주수
10 - (long) 대차잔고금액

7254
0 - (long) 일자 - 잠정치인 경우 날짜가 아닌 시간으로 표시
1 - (long) 개인
2 - (long) 외국인
3 - (long) 기관계
4 - (long) 금융투자
5 - (long) 보험
6 - (long) 투신
7 - (long) 은행
8 - (long) 기타금융
9 - (long) 연기금 등
10 - (long) 기타법인
11 - (long) 기타외인
12 - (long) 사모펀드
13 - (long) 국가지자체
14 - (long) 종가
15 - (long) 대비
16 - (double) 대비율
17 - (long) 거래량
18 - (char) 확정치여부 ('0' : 잠정치, '1': 확정치)
