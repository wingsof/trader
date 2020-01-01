from gevent import monkey; monkey.patch_all()
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.join(*(['..' + os.sep] * 2)))))

from PyQt5.QtWidgets import QApplication
import mainwidget
from morning_server import message, stream_readwriter
import socket
import gevent


def mainloop(app):
    while True:
        app.processEvents()
        while app.hasPendingEvents():
            app.processEvents()
            gevent.sleep()
        gevent.sleep()


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)

    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()

    app = QApplication(sys.argv)
    w = mainwidget.MainWidget()
    app.installEventFilter(w.action)
    w.show()

    gevent.joinall([gevent.spawn(mainloop, app)])
