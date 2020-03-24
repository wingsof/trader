import sys
import os
from win32com.client import makepy


def run():
    CYBOS_PLUS_DIR = r"c:\daishin\CYBOSPLUS"
    DLL_FILES = ['cpdib.dll',
                'CpForeDib.dll',
                'CpForeTrade.dll',
                'CpForeUtil.dll',
                'CpGmaxDib.dll',
                'CpIndexes.dll',
                'CpintTrade.dll',
                'CpNanoSysDib.dll',
                'CpPrivDib.dll',
                'CpSysDib.dll',
                'cptrade.dll',
                'cputil.dll']
    for i, f in enumerate(DLL_FILES):
        DLL_FILES[i] = os.path.join(CYBOS_PLUS_DIR, f) 

    sys.argv = ['makepy']
    sys.argv.extend(DLL_FILES)
    makepy.main()

# Check whether file is created on gen folder


if __name__ == '__main__':
    run()
