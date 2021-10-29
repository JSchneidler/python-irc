import socket
import threading


from client.TCPClient import TCPClient


PORT = 1944


def fakeServer():
    """Accept a TCP connection then close."""
    server = socket.socket()
    server.settimeout(1)  # Close server if no connection is made after 1s
    server.bind(("", PORT))
    server.listen(0)
    server.accept()
    server.close()


def test_TCPClient_connect():
    serverThread = threading.Thread(target=fakeServer)
    serverThread.start()

    client = TCPClient("localhost", PORT)
    client.connect()
    client.close()

    # Close server thread
    serverThread.join()
