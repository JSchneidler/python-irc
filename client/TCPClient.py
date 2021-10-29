import socket


class TCPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send(self, data):
        self.sock.send(data.encode())

    def receive(self):
        return self.sock.recv(1024).decode()

    def close(self):
        self.sock.close()
