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



if __name__ == '__main__':
    ds = DataStream()
    print(str(ds))

    from datetime import datetime
    ds = DataStream('cybos_stock_realtime', False, datetime.now(), datetime.now())
    print(ds)