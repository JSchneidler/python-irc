import threading
from socketserver import BaseRequestHandler, ThreadingTCPServer

from client.IRCClient import IRCClient


SERVER_HOST = "localhost"
SERVER_PORT = 6666


def test_IRCClient_connect():
    server = ThreadingTCPServer((SERVER_HOST, SERVER_PORT), BaseRequestHandler)
    serverThread = threading.Thread(target=server.serve_forever)
    serverThread.start()

    client = IRCClient(SERVER_HOST, SERVER_PORT)
    client.connect()
    client.disconnect()

    # Close server
    server.shutdown()
    serverThread.join()
