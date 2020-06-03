import json
import sys

if len(sys.argv) < 8:
    print('Usage:', sys.argv[0], 'client_name password certificate_password mongo_id mongo_password server_ip capability collector_count')
    print('capability(request,trade)')
    sys.exit(1)

client = dict()
client['client_name'] = sys.argv[1]
client['password'] = sys.argv[2]
client['certificate_password'] = sys.argv[3]
client['mongo_id'] = sys.argv[4]
client['mongo_password'] = sys.argv[5]
client['server_ip'] = sys.argv[6]
client['capability'] = sys.argv[7]
client['collector_count'] = sys.argv[7]


with open('client_info.json', 'w') as outfile:
    json.dump(client, outfile)
