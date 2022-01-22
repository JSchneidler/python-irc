from dataclasses import dataclass
from threading import Lock
from typing import Optional
from datetime import datetime

from lib.logger import logger
from lib.User import User
from lib.Channel import Channels

from .ClientHandler import ClientHandler


class ClientNotFound(Exception):
    pass


@dataclass
class Client:
    handler: ClientHandler
    user: User

    def getIdentifier(self) -> str:
        return f"{self.user.nick}!{self.user.username}@{self.handler.getHost()}"


@dataclass
class OperatorCredential:
    userHash: bytes
    passwordHash: bytes


Clients = dict[str, Client]
OperatorCredentials = list[OperatorCredential]
MOTD = list[str]


def _getAnonymousIdentifier(handler: ClientHandler) -> str:
    return f"{handler.getHost()}:{handler.getPort()}"


log = logger.getChild("server.ServerState")


class ServerState:
    host: str
    port: int
    motd: MOTD
    operatorCredentials: OperatorCredentials
    createdDate: str
    channels: Channels
    clients: Clients
    newClients: Clients
    usersDisabled: bool

    lock: Lock

    def __init__(
        self,
        host: str,
        port: int,
        motd: Optional[MOTD],
        operatorCredentials: Optional[OperatorCredentials],
        createdDate: Optional[str],
    ) -> None:
        self.host = host
        self.port = port
        self.motd = motd or []
        self.operatorCredentials = operatorCredentials or []
        self.createdDate = createdDate or datetime.now().isoformat()
        self.channels = {}
        self.clients = {}
        self.newClients = {}
        self.usersDisabled = False

        self.lock = Lock()

    def addUser(self, handler: ClientHandler) -> None:
        with self.lock:
            user = User()
            client = Client(handler, user)
            self.newClients[_getAnonymousIdentifier(handler)] = client
            handler.user = user

    def removeUser(self, handler: ClientHandler) -> None:
        with self.lock:
            if handler.user and handler.user.username:
                log.info(f"Removing user {handler.user.nick}")
                for channelName in self.channels:
                    channel = self.channels[channelName]
                    if handler.user.username in channel.getAllUsers():
                        channel.removeUser(handler.user)
                del self.clients[handler.user.username]
            elif _getAnonymousIdentifier(handler) in self.newClients:
                del self.newClients[_getAnonymousIdentifier(handler)]
            else:
                raise ClientNotFound(handler)

    def getClient(self, handler: ClientHandler) -> Client:
        if handler.user and handler.user.username:
            return self.clients[handler.user.username]
        else:
            return self.newClients[_getAnonymousIdentifier(handler)]

    def getUserFromNick(self, nick: str) -> User:
        return self.getClientFromNick(nick).user

    def getClientFromNick(self, nick: str) -> Client:
        return next(c for c in self.clients.values() if c.user.nick == nick)

    def userAlreadyRegistered(self, user: User) -> bool:
        return user.password is not None

    def getPrefix(self) -> str:
        return f":{self.host}"
