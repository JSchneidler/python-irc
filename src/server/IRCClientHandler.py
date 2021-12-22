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

        logging.info("New connection from {}".format(self.client_address))

        self.server.addUser(self)

    def handle(self) -> None:
        while True:
            line = self.rfile.readline().strip().decode("utf-8")

            if len(line) > 0:
                logging.debug("{} wrote: {}".format(self.client_address, line))
                self.server.handleMessage(self, line)
            else:
                break

    def send(self, message: str) -> None:
        self.wfile.write(message.encode("utf-8"))

    def finish(self) -> None:
        logging.info("Connection from {} closed".format(self.client_address))
        self.server.removeUser(self)

        super().finish()

    def getHost(self) -> str:
        return self.client_address[0]

    def getPort(self) -> int:
        return self.client_address[1]