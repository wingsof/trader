
last_msg = []


def stream_write(sock, header, body, manager = None):
    global last_msg
    last_msg.append((sock, header, body))
