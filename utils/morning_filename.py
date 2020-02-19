from datetime import datetime
import os
import os.path


def get_log_filename(is_stderr):
    prefix = datetime.now().strftime('%Y%m%d')
    if is_stderr:
        ext = '_err.log'
    else:
        ext = '.log'

    path = ''
    try:
        path = os.environ['MORNING_PATH'] + os.sep + 'logs' + os.sep
    except KeyError:
        print('NO MORNING_PATH SYSTEM ENVIRONMENT VARIABLE') 
    start_index = 0
    filename = path + prefix + ext

    while os.path.exists(filename):
        start_index += 1
        filename = path + prefix + '_' + str(start_index) + ext
    return filename


