from socketserver import BaseRequestHandler, ThreadingTCPServer
import logging

from irc.IRCChannel import IRCChannel, Channels
from irc.IRCUser import IRCUser, Users


class IRCClientHandler(BaseRequestHandler):
    user: IRCUser = None

    def setup(self) -> None:
        logging.info("New connection from {}".format(self.client_address))

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        logging.info("{} wrote:".format(self.client_address[0]))
        logging.info(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

    def finish(self) -> None:
        logging.info("Connection from {} closed".format(self.client_address))


# https://datatracker.ietf.org/doc/html/rfc1459#section-1.1
class IRCServer(ThreadingTCPServer):
    """An IRC server"""

    host: str
    port: int
    started: bool = False

    channels: Channels = {}
    users: Users = {}
    ops: Users = {}
    motd: str

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        super().__init__((host, port), IRCClientHandler)

    def start(self) -> None:
        """Starts the server"""
        if not self.started:
            self.started = True
            logging.info("Server listening on {}:{}".format(self.host, self.port))
            self.serve_forever()

    def stop(self) -> None:
        """Stops the server"""
        if self.started:
            self.started = False
            self.shutdown()
            self.server_close()

    def server_close(self) -> None:
        """Server cleanup"""
        logging.info("Server stopped")
        pass
