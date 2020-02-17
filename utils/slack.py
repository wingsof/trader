import os
import slack
from datetime import datetime

def send_slack_message(msg):
    client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])
    response = client.chat_postMessage(
        channel='#trading',
        text=datetime.now().strftime('%Y%m%d:%H%M%S') + ') ' + msg)
    #assert response["ok"]
    #assert response["message"]["text"] == "Hello world!"

if __name__ == '__main__':
    send_slack_message('hello world')
