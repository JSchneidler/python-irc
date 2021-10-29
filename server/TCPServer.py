import socket


class TCPServer:
    host: str
    port: int

    def __init__(self, host: str, port: int) -> None:
        """Sets up a TCPServer instance"""
        self.host = host
        self.port = port

    def start(self) -> None:
        """Starts the server"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print("Connected by", addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.sendall(data)
                    print(data)
