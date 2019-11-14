

import chooser
from datetime import datetime

class KosdaqCurrentBullCodes(chooser.Chooser):
    def __init__(self, is_repeat = False, from_date = datetime.now(), until_date = datetime.now(), repeat_msec = 0):
        print(is_repeat, from_date, until_date, repeat_msec)
                cp7043.Cp7043().request(self.codes)
        if len(self.codes) == 0:
            print('CODE LOAD failed')
            return False


if __name__ == '__main__':
    kosdaq = KosdaqCurrentBullCodes(is_repeat = True, repeat_msec = 6000)