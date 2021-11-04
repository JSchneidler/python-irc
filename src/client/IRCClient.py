import socket

from irc.IRCChannel import IRCChannel, Channels
from irc.IRCUser import IRCUser, Users


# https://datatracker.ietf.org/doc/html/rfc1459#section-1.2
class IRCClient:
    """An IRC client"""

    host: str
    port: int
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    channels: Channels = {}
    user: IRCUser
    users: Users = {}

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def connect(self) -> None:
        """Connects to the server"""
        self.client.connect((self.host, self.port))

    def disconnect(self) -> None:
        """Disconnects from the server"""
        # self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
