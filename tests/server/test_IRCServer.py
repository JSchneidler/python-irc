import socket
import threading

from server.IRCServer import IRCServer


SERVER_HOST = "localhost"
SERVER_PORT = 6666


def test_IRCServer_connect():
    server = IRCServer(SERVER_HOST, SERVER_PORT)
    serverThread = threading.Thread(target=server.start)
    serverThread.start()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))
    client.close()

    # Close server
    server.stop()
    serverThread.join()


def test_IRCServer_connectMultipleClients():
    server = IRCServer(SERVER_HOST, SERVER_PORT)
    serverThread = threading.Thread(target=server.start)
    serverThread.start()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))
    client2.connect((SERVER_HOST, SERVER_PORT))
    client.close()
    client2.close()

    # Close server
    server.stop()
    serverThread.join()
