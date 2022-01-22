from socket import socket, AF_INET, SOCK_STREAM

from lib.logger import logger
from lib.Channel import Channels

log = logger.getChild("client.Client")


# https://datatracker.ietf.org/doc/html/rfc1459#section-1.2
class Client:
    host: str
    port: int
    client: socket

    channels: Channels

    def __init__(self, host: str, port: int) -> None:
        self.channels = {}

        self.host = host
        self.port = port
        self.client = socket(AF_INET, SOCK_STREAM)

    def connect(self) -> None:
        """Connects to the server"""
        self.client.connect((self.host, self.port))
        log.info("Connected to server at " + self.host + ":" + str(self.port))

    def disconnect(self) -> None:
        """Disconnects from the server"""
        # self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        log.info("Disconnected from server")
