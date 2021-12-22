from socketserver import StreamRequestHandler
from typing import TYPE_CHECKING
import logging

from irc.IRCUser import User

if TYPE_CHECKING:
    from .IRCServer import Server

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


class ClientHandler(StreamRequestHandler):
    user: User = None

    # Inherited from StreamRequestHandler
    server: "Server"

    def setup(self) -> None:
        super().setup()

        logging.debug("New connection from {}".format(self.getClientAddress()))

        self.server.addUser(self)

    def handle(self) -> None:
        while True:
            line = self.rfile.readline().strip().decode("utf-8")

            if len(line) > 0:
                logging.debug("{} wrote: {}".format(self.getClientAddress(), line))
                self.server.handleMessage(self, line)
            else:
                break

    def send(self, message: str) -> None:
        self.wfile.write(message.encode("utf-8"))
        logging.debug("Server wrote to {}: {}".format(self.getClientAddress(), message))

    def finish(self) -> None:
        logging.debug("Connection from {} closed".format(self.getClientAddress()))
        self.server.removeUser(self)

        super().finish()

    def getClientAddress(self) -> str:
        return "{}:{}".format(self.getHost(), self.getPort())

    def getHost(self) -> str:
        return self.client_address[0]

    def getPort(self) -> int:
        return self.client_address[1]
