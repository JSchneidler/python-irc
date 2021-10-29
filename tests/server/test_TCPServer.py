import socket
import threading


from server.TCPServer import TCPServer


PORT = 1944


def fakeClient():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", PORT))
    client.close()


def test_TCPServer_connect():
    server = TCPServer("", PORT)
    serverThread = threading.Thread(target=server.start)
    serverThread.start()

    fakeClient()

    serverThread.join()
