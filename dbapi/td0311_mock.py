import string
import random


class Td0311:
    def __init__(self, obj_id):
        self.obj_id = obj_id
        self.order_type = ''
        self.account_num = ''
        self.account_type = ''
        self.code = ''
        self.quantity = 0
        self.price = 0

    def SetInputValue(index, value):
        pass


    def BlockRequest(self):
        pass

    def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def GetHeaderValue(self, index):
        if index == 0:
            return '0'
        elif index == 1:
            return self.account_num
        elif index == 2:
            return self.account_type
        elif index == 3:
            return self.code
        elif index == 4:
            return self.quantity
        elif index == 5:
            return self.price
        elif index == 8:
            return self.id_generator()
        elif index == 9:
            return 'nnnlife'
        elif index == 10:
            return 'myname'
        elif index == 12:
            return 'order_type'
        return 0
