from datetime import datetime


class DataStream:        
    def __init__(self, stream_name = 'Unknown', is_realtime = True, from_datetime = None, until_datetime = None):
        self.stream_name = stream_name
        self.is_realtime = is_realtime
        self.from_datetime = from_datetime
        self.until_datetime = until_datetime

    def __str__(self):
        if self.is_realtime:
            return self.stream_name + '/' + str(self.is_realtime)

        return self.stream_name + '/' + str(self.is_realtime) + '/' + str(self.from_datetime) + '/' + str(self.until_datetime)

    @staticmethod
    def factory(self, stream_desc):
        tokens = stream_desc.split('/')
        if len(tokens) < 2:
            return None

        stream_name = tokens[0]
        is_realtime = bool(tokens[1])
        from_datetime = None
        until_datetime = None
        if len(tokens) == 4:
            from_datetime = datetime.fromisoformat(tokens[2])
            until_datetime = datetime.fromisoformat(tokens[3])

        if tokens[0] == 'cybos_stock_tick':
            import cybos_stock_tick
            if is_realtime:
                return cybos_stock_tick.CybosStockTick()
            elif len(tokens) == 4:
                pass # TODO: create DB api for querying
        elif tokens[0] == 'cybos_stock_ba_tick':
            import cybos_stock_ba_tick
            if is_realtime:
                return cybos_stock_ba_tick.CybosStockBaTick()
        return None


if __name__ == '__main__':
    ds = DataStream()
    print(str(ds))

    from datetime import datetime
    ds = DataStream('cybos_stock_realtime', False, datetime.now(), datetime.now())
    print(ds)