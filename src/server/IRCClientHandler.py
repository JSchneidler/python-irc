from socketserver import StreamRequestHandler
from typing import TYPE_CHECKING, Optional

from irc.logger import logger
from irc.IRCUser import User


if TYPE_CHECKING:
    from .IRCServer import Server


log = logger.getChild("server.IRCClientHandler")


class ClientHandler(StreamRequestHandler):
    user: Optional[User]

    # Inherited from StreamRequestHandler
    server: "Server"

    def setup(self) -> None:
        super().setup()
        self.user = None

        log.debug(f"New connection from {self.getClientAddress()}")

        self.server.addUser(self)

    def handle(self) -> None:
        while True:
            try:
                line = self.rfile.readline().strip().decode()

                if len(line) > 0:
                    log.debug(f"{self.getClientAddress()} wrote: {line}")
                    self.server.handleMessage(self, line)
                else:
                    break
            except ConnectionResetError:
                break

    def send(self, message: str) -> None:
        message = message + "\r\n"
        self.wfile.write(message.encode())
        log.debug(
            f"Server wrote to {self.getClientAddress()}: {repr(message)}"
        )

    def finish(self) -> None:
        log.debug(f"Connection from {self.getClientAddress()} closed")
        self.server.removeUser(self)

        super().finish()

    def getClientAddress(self) -> str:
        return f"{self.getHost()}:{self.getPort()}"

    def getHost(self) -> str:
        return self.client_address[0]

    def getPort(self) -> int:
        return self.client_address[1]
