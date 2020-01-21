import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configs import client_info

HOME_MONGO_ADDRESS = ('mongodb://' + client_info.get_mongo_id() + ':' + 
                        client_info.get_mongo_password() + '@' + 
                        client_info.get_server_ip() + ':27017')


if __name__ == '__main__':
    print(HOME_MONGO_ADDRESS)
