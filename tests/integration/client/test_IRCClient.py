import threading
from socketserver import BaseRequestHandler, ThreadingTCPServer

from client.IRCClient import Client


SERVER_HOST = "localhost"
SERVER_PORT = 0


def test_Client_connect():
    server = ThreadingTCPServer((SERVER_HOST, SERVER_PORT), BaseRequestHandler)
    serverThread = threading.Thread(target=server.serve_forever)
    serverThread.start()

    client = Client(server.server_address[0], server.server_address[1])
    client.connect()
    client.disconnect()

    # Close server
    server.shutdown()
    serverThread.join()
