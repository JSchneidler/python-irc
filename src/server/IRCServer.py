from socketserver import ThreadingTCPServer
from typing import NamedTuple
import logging

from irc.IRCChannel import Channels
from irc.IRCUser import User
from irc.IRCMessage import Message

from .IRCClientHandler import ClientHandler
from . import Reply


class ClientNotFoundException(Exception):
    pass


class ParamValidationException(Exception):
    pass


class Client(NamedTuple):
    handler: ClientHandler
    user: User


Clients = dict[str, Client]


class Server(ThreadingTCPServer):
    host: str = None
    port: int = None
    started: bool = False

    motd: list[str] = None
    createdDate: str = None
    channels: Channels = {}
    clients: Clients = {}
    newClients: Clients = {}

    def __init__(self, host: str, port: int, motd: list[str] = None) -> None:
        super().__init__((host, port), ClientHandler)

        self.daemon_threads = True
        self.host = self.server_address[0]
        self.port = self.server_address[1]
        self.motd = motd

    def start(self) -> None:
        if not self.started:
            self.started = True
            logging.info("Server listening on {}:{}".format(self.host, self.port))
            self.serve_forever()

    def stop(self) -> None:
        super().shutdown()
        self.started = False
        logging.info("Server stopped")

    def getHost(self) -> str:
        return self.host

    def addUser(self, handler: ClientHandler) -> None:
        user = User()
        self.newClients[getAnonymousIdentifier(handler)] = Client(handler, user)
        handler.user = user

    def removeUser(self, handler: ClientHandler) -> None:
        if handler.user.username:
            del self.clients[handler.user.username]
        elif getAnonymousIdentifier(handler) in self.newClients:
            del self.newClients[getAnonymousIdentifier(handler)]
        else:
            raise ClientNotFoundException(handler)

    def handleMessage(self, handler: ClientHandler, rawMessage: str) -> None:
        client = self._getClient(handler)
        message = Message(rawMessage, client.user)
        if message.command == "CAP":
            self._handleCap(client)
        elif message.command == "PASS":
            self._handlePass(client, message)
        elif message.command == "NICK":
            self._handleNick(client, message)
        elif message.command == "USER":
            self._handleUser(client, message)
        elif message.command == "JOIN":
            logging.info("Unhandled command: {}".format(message.rawMessage))
        elif message.command == "QUIT":
            pass
        elif message.command == "PART":
            logging.info("Unhandled command: {}".format(message.rawMessage))
        elif message.command == "PRIVMSG":
            logging.info("Unhandled command: {}".format(message.rawMessage))
        elif message.command == "MODE":
            logging.info("Unhandled command: {}".format(message.rawMessage))
        elif message.command == "TOPIC":
            logging.info("Unhandled command: {}".format(message.rawMessage))
        elif message.command == "PING":
            logging.info("Unhandled command: {}".format(message.rawMessage))
        elif message.command == "PONG":
            logging.info("Unhandled command: {}".format(message.rawMessage))
        elif message.command == "ERROR":
            logging.info("Unhandled command: {}".format(message.rawMessage))
        elif message.command == "MOTD":
            self._sendMotd(client)
        elif message.command == "LUSERS":
            self._sendLUsers(client)
        else:
            logging.info("Unhandled command: {}".format(message.rawMessage))

    def _getClient(self, handler: ClientHandler) -> Client:
        if handler.user.username:
            return self.clients.get(handler.user.username)
        else:
            return self.newClients.get(getAnonymousIdentifier(handler))

    # https://ircv3.net/specs/extensions/capability-negotiation
    def _handleCap(self, client: Client) -> None:
        client.handler.send("CAP * LS :")

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.1
    def _handlePass(self, client: Client, message: Message) -> None:
        try:
            self._requireParams(client, message)
            if self._userAlreadyRegistered(client.user):
                client.handler.send(self._makeReply(client, Reply.alreadyRegistered()))
            else:
                client.user.password = message.params[0]
        except ParamValidationException:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.2
    def _handleNick(self, client: Client, message: Message) -> None:
        if len(message.params) == 0:
            client.handler.send(self._makeReply(client, Reply.noNickGiven()))
        else:
            nick = message.params[0]
            try:
                next(c for c in self.clients.values() if c.user.nick == nick)
                client.handler.send(self._makeReply(client, Reply.nickInUse(nick)))
            except StopIteration:
                client.user.nick = nick

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.3
    def _handleUser(self, client: Client, message: Message) -> None:
        try:
            self._requireParams(client, message, 4)
            if client.user.username:
                client.handler.send(self._makeReply(client, Reply.alreadyRegistered()))
            else:
                client.user.username = message.params[0]
                client.user.mode = message.params[1]
                client.user.realname = " ".join(message.params[3:])

                self._sendWelcome(client)

                self.clients[client.user.username] = client
                del self.newClients[getAnonymousIdentifier(client.handler)]
                logging.info(
                    "Registered user {} from {}".format(
                        client.user.username, client.handler.getClientAddress()
                    )
                )
        except ParamValidationException:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2813#section-5.2.1
    def _sendWelcome(self, client: Client) -> None:
        replies = [
            Reply.welcome(
                client.user.nick, client.user.username, client.handler.getHost()
            ),
            Reply.yourHost(self.host, "0.0.1"),
            Reply.created(self.createdDate),
            Reply.myInfo(
                client.handler.getHost(), "0.0.1", "aiwroOs", "OovaimnqpsrtklbeI"
            ),
        ]
        for reply in replies:
            client.handler.send(self._makeReply(client, reply))
        self._sendLUsers(client)
        self._sendMotd(client)

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.4.1
    def _sendMotd(self, client: Client) -> None:
        client.handler.send(self._makeReply(client, Reply.motdStart(self.host)))
        if self.motd:
            for line in self.motd:
                client.handler.send(self._makeReply(client, Reply.motd(line)))
        client.handler.send(self._makeReply(client, Reply.endOfMotd()))

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.4.2
    def _sendLUsers(self, client: Client) -> None:
        replies = [
            Reply.lUserClient(len(self.clients), 0),
            Reply.lUserOp(len(self.clients)),  # TODO: Implement ops
            Reply.lUserUnknown(len(self.newClients)),
            Reply.lUserChannels(len(self.channels)),
            Reply.lUserMe(len(self.clients)),
        ]
        for reply in replies:
            client.handler.send(self._makeReply(client, reply))

    def _requireParams(
        self, client: Client, message: Message, paramCount: int = 1
    ) -> None:
        if (not message.params) or (len(message.params) < paramCount):
            client.handler.send(
                self._makeReply(client, Reply.needMoreParams(message.command))
            )
            raise ParamValidationException(message.command)

    def _makeReply(self, client: Client, reply: Reply.Reply) -> str:
        return f"{self._getPrefix()} {client.user.username} {reply.code} {reply.text}"

    def _userAlreadyRegistered(self, user: User) -> bool:
        return user.password is not None

    def _getPrefix(self) -> str:
        return f":{self.host}"


def getAnonymousIdentifier(clientHandler: ClientHandler) -> str:
    return f"{clientHandler.getHost()}:{clientHandler.getPort()}"
