import win32com.client


class Connection:
    def __init__(self):
        self.obj = win32com.client.Dispatch("CpUtil.CpCybos")

    # return example: 14906
    def get_remain_time(self):
        return self.obj.LimitRequestRemainTime

    def realtime_left_count(self):
        return self.obj.GetLimitRemainCount(2)

    def request_left_count(self):
        return self.obj.GetLimitRemainCount(1)

    def order_left_count(self):
        return self.obj.GetLimitRemainCount(0)

    def is_connected(self):
        return self.obj.IsConnect


if __name__ == '__main__':
    conn = Connection()
    print(conn.is_connected())

    if conn.is_connected():
        import stock_chart
        #chart = stock_chart.StockChart('A005930')
        #for data in chart.get_by_date(20181018):
        #    print(data)
        print("Remain Time", conn.get_remain_time())
        print("Realtime", conn.realtime_left_count())
        print("Request", conn.request_left_count())
        print("Order", conn.order_left_count())
