from datetime import datetime

class TimeManager:
    def __init__(self):
        pass

    def is_runnable(self, t=datetime.now()):
        if t.hour >= 6 and t.hour <= 15:
            return True
        return False

    def is_order_collect_time(self, t=datetime.now()):
        if t.hour is 15 and t.minute > 20 and t.minute <= 27:
            return True
        return False

    def is_order_start_time(self, t=datetime.now()):
        if t.hour is 15 and t.minute > 27 and t.minute < 30:
            return True
        return False
    
    def is_order_wait_done_time(self, t=datetime.now()):
        if t.hour is 16 and t.minute > 30:
            return True
        return False

    def get_today(self):
        n = datetime.now()
        return datetime(n.year, n.month, n.day)

    def get_heart_beat(self):
        return 1000
