from socketserver import ThreadingTCPServer
from typing import Optional

from lib.logger import logger
from lib.Message import Message

from .ServerState import ServerState, MOTD, OperatorCredentials
from .ClientHandler import ClientHandler
from .MessageHandlers.handlers import HANDLERS


log = logger.getChild("server.Server")


class Server(ThreadingTCPServer):
    started: bool

    serverState: ServerState

    def __init__(
        self,
        host: str,
        port: int,
        motd: Optional[MOTD] = [],
        operatorCredentials: Optional[OperatorCredentials] = [],
        createdDate: Optional[str] = None,
    ) -> None:
        super().__init__((host, port), ClientHandler)

        host = self.server_address[0]
        port = self.server_address[1]

        self.serverState = ServerState(
            host, port, motd, operatorCredentials, createdDate
        )
        self.started = False

    def start(self) -> None:
        if not self.started:
            self.started = True
            log.info(
                f"Server listening on {self.serverState.host}:{self.serverState.port}"
            )
            self.serve_forever()

    def stop(self) -> None:
        self.shutdown()
        self.started = False
        log.info("Server stopped")

    def handleClientConnect(self, handler: ClientHandler) -> None:
        self.serverState.addUser(handler)

    def handleClientDisconnect(self, handler: ClientHandler) -> None:
        self.serverState.removeUser(handler)

    def handleMessage(self, handler: ClientHandler, rawMessage: str) -> None:
        client = self.serverState.getClient(handler)
        message = Message(rawMessage, client.user)

        if message.command in HANDLERS:
            Handler = HANDLERS[message.command]
            messageHandler = Handler(self.serverState, client)
            messageHandler.handle(message)
        elif message.command == "QUIT":
            pass
        else:
            log.debug(f"Unhandled command: {message.rawMessage}")
