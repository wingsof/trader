


if __name__ == '__main__':
    trader = Trader(True)
    # selector 는 실시간으로 항목을 추가할 수 있다
    trader.set_selector(KosdaqCurrentBullCodes(True, 60000))

    trader.set_executor(CybosAccount())

    # 스트림 간 동기화 어떻게 맞출 것인가? 시작시간, 종료시간 -> Main Clock은 다음 같이 연결된 Pipeline에 시간을 제공해야 한다
    # 마지막 data stream 인지 어떻게 알릴 것인가?
    # 아래 경우, 스트림 output 은 2개로 나온다
    trader.set_stream_pipeline([(CybosStockRealtime.name, CybosStockRealtimeConverter.name),
                                (CybosStockBaRealtime.name, CybosStockBaRealtimeConverter.name)])

    # 스트림에서는 하나의 데이터만 나올 수 있고, 필터를 거치고 나서는 배열로 나온다
    trader.set_filter_pipeline(0, [CybosInMarketRemoveFirstFilter.name, CybosStockRealtimeMinBuffer.name])
    trader.set_filter_pipeline(1, [CybosStockBaInMarketFilter.name])

    trader.set_strategy_pipeline(0, [TickCybosThreeMinUp.name, TickCybosBuySellAccDiff.name], CybosAndDecision.name)
    trader.set_strategy_pipeline(1, [TickCybosDecisionByTakeLast.name])

    trader.set_decision(MongoStockRealRecord.name)
    
    trader.run()