from socketserver import ThreadingTCPServer
from typing import NamedTuple
from datetime import datetime

from irc.logger import logger
from irc.IRCChannel import Channels, Channel
from irc.IRCUser import User
from irc.IRCMessage import Message

from .IRCClientHandler import ClientHandler
from . import Reply


log = logger.getChild("server.IRCServer")


class ClientNotFound(Exception):
    pass


class FailedParamValidation(Exception):
    pass


class Client(NamedTuple):
    handler: ClientHandler
    user: User


Clients = dict[str, Client]


class Server(ThreadingTCPServer):
    host: str
    port: int
    started: bool = False

    motd: list[str]
    createdDate: str
    channels: Channels = {}
    clients: Clients = {}
    newClients: Clients = {}

    def __init__(
        self,
        host: str,
        port: int,
        motd: list[str] = [],
        createdDate: str = datetime.now().isoformat(),
    ) -> None:
        super().__init__((host, port), ClientHandler)

        self.daemon_threads = True
        self.host = self.server_address[0]
        self.port = self.server_address[1]
        self.motd = motd
        self.createdDate = createdDate

    def start(self) -> None:
        if not self.started:
            self.started = True
            log.info(f"Server listening on {self.host}:{self.port}")
            self.serve_forever()

    def stop(self) -> None:
        super().shutdown()
        self.started = False
        log.info("Server stopped")

    def addUser(self, handler: ClientHandler) -> None:
        user = User()
        client = Client(handler, user)
        self.newClients[getAnonymousIdentifier(handler)] = client
        handler.user = user

    def removeUser(self, handler: ClientHandler) -> None:
        if handler.user and handler.user.username:
            log.info(f"Removing user {handler.user.username}")
            for channelName in self.channels:
                channel = self.channels[channelName]
                channel.removeUser(handler.user)
            del self.clients[handler.user.username]
        elif getAnonymousIdentifier(handler) in self.newClients:
            del self.newClients[getAnonymousIdentifier(handler)]
        else:
            raise ClientNotFound(handler)

    def handleMessage(self, handler: ClientHandler, rawMessage: str) -> None:
        client = self._getClient(handler)
        message = Message(rawMessage, client.user)
        if message.command == "QUIT":
            pass
        elif message.command == "CAP":
            self._handleCap(client)
        elif message.command == "PASS":
            self._handlePass(client, message)
        elif message.command == "NICK":
            self._handleNick(client, message)
        elif message.command == "USER":
            self._handleUser(client, message)
        elif message.command == "JOIN":
            self._handleJoin(client, message)
        elif message.command == "PART":
            self._handlePart(client, message)
        elif message.command == "MODE":
            self._handleMode(client, message)
        elif message.command == "TOPIC":
            self._handleTopic(client, message)
        elif message.command == "NAMES":
            self._handleNames(client, message)
        elif message.command == "LIST":
            self._handleList(client, message)
        elif message.command == "KICK":
            self._handleKick(client, message)
        elif message.command == "PRIVMSG":
            self._handlePrivMsg(client, message)
        elif message.command == "PING":
            self._handlePing(client)
        elif message.command == "ERROR":
            log.debug(f"Unhandled command: {message.rawMessage}")
        elif message.command == "MOTD":
            self._sendMotd(client)
        elif message.command == "LUSERS":
            self._sendLUsers(client)
        else:
            log.debug(f"Unhandled command: {message.rawMessage}")

    def _getClient(self, handler: ClientHandler) -> Client:
        if handler.user and handler.user.username:
            return self.clients[handler.user.username]
        else:
            return self.newClients[getAnonymousIdentifier(handler)]

    def _getUserFromNick(self, nick: str) -> User:
        return next(
            c.user for c in self.clients.values() if c.user.nick == nick
        )

    # https://ircv3.net/specs/extensions/capability-negotiation
    def _handleCap(self, client: Client) -> None:
        client.handler.send("CAP * LS :")

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.1
    def _handlePass(self, client: Client, message: Message) -> None:
        try:
            self._requireParams(client, message)
            if self._userAlreadyRegistered(client.user):
                self._replyNumeric(client, Reply.alreadyRegistered())
            else:
                client.user.password = message.params[0]
        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.2
    def _handleNick(self, client: Client, message: Message) -> None:
        if len(message.params) == 0:
            self._replyNumeric(client, Reply.noNickGiven())
        else:
            nick = message.params[0]
            try:
                next(c for c in self.clients.values() if c.user.nick == nick)
                self._replyNumeric(client, Reply.nickInUse(nick))
            except StopIteration:
                log.info(f"Changing nick from {client.user.nick} to {nick}")
                client.user.nick = nick

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.3
    def _handleUser(self, client: Client, message: Message) -> None:
        try:
            self._requireParams(client, message, 4)
            if client.user.username:
                self._replyNumeric(client, Reply.alreadyRegistered())
            else:
                client.user.username = message.params[0]
                client.user.mode = int(message.params[1])
                client.user.realname = " ".join(message.params[3:])

                self._sendWelcome(client)

                self.clients[client.user.username] = client
                del self.newClients[getAnonymousIdentifier(client.handler)]
                log.info(
                    (
                        f"Registered user {client.user.username}"
                        f" from {client.handler.getClientAddress()}"
                    )
                )
        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.1
    def _handleJoin(self, client: Client, message: Message) -> None:
        try:
            self._requireParams(client, message)

            # Leave all channels
            if message.params[0] == "0":
                for channelName in self.channels:
                    channel = self.channels[channelName]
                    if client.user.username in channel.getAllUsers():
                        channel.removeUser(client.user)
            else:
                channels = message.params[0].split(",")
                try:
                    keys = message.params[1].split(",")
                except IndexError:
                    keys = None

                for i, channelName in enumerate(channels):
                    key = None
                    if keys and len(keys) > i:
                        key = keys[i]

                    if channelName in self.channels:
                        channel = self.channels[channelName]
                        if channel.key and key != channel.key:
                            self._replyNumeric(
                                client, Reply.badChannelKey(channelName)
                            )
                            break
                        channel.addUser(client.user)
                    else:
                        channel = Channel(channelName, client.user, key)
                        self.channels[channelName] = channel
                    self._sendToChannel(client, channel, f"JOIN {channelName}")
                    self._replyNumeric(client, Reply.topic(channel))
                    self._replyNumeric(client, Reply.names(channel))
                    self._replyNumeric(
                        client, Reply.endOfNames(channelName, client.user)
                    )
        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.2
    def _handlePart(self, client: Client, message: Message) -> None:
        try:
            self._requireParams(client, message)

            channels = message.params[0].split(",")
            try:
                partMessage = message.params[1].lstrip(":")
            except IndexError:
                partMessage = None

            for channelName in channels:
                if channelName in self.channels:
                    channel = self.channels[channelName]
                    msg = f"PART {message.params[0]}"
                    if partMessage:
                        msg += f" :{partMessage}"
                    self._sendToChannel(client, channel, msg)
                    channel.removeUser(client.user)
                    # TODO: If no users in channel, delete channel
        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.3
    def _handleMode(self, client: Client, message: Message) -> None:
        try:
            self._requireParams(client, message)

            channelName = message.params[0]
            if channelName in self.channels:
                self._replyNumeric(client, Reply.noChannelModes(channelName))

        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.4
    def _handleTopic(self, client: Client, message: Message):
        try:
            self._requireParams(client, message)

            channelName = message.params[0]
            try:
                topic = " ".join(message.params[1:]).lstrip(":")
            except IndexError:
                topic = None

            if channelName in self.channels:
                channel = self.channels[channelName]
                if topic:
                    channel.setTopic(topic)
                    client.handler.send(
                        (
                            f":{client.user.nick}"
                            f" TOPIC {channel.name}"
                            f" :{channel.topic}"
                        )
                    )
                    log.info(
                        (
                            f"User {client.user.nick}"
                            f" changed topic of channel {channel.name}"
                            f" to {channel.topic}"
                        )
                    )
                else:
                    self._replyNumeric(client, Reply.topic(channel))
            else:
                # TODO: ERR_NOTONCHANNEL?
                pass
        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.5
    def _handleNames(self, client: Client, message: Message):
        channels = message.params[0].split(",")

        for channelName in channels:
            if channelName in self.channels:
                channel = self.channels[channelName]
                self._replyNumeric(client, Reply.names(channel))

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.6
    def _handleList(self, client: Client, message: Message):
        channels: list[str] | Channels
        try:
            channels = message.params[0].split(",")
        except IndexError:
            channels = self.channels

        for channelName in channels:
            channel = self.channels[channelName]
            client.handler.send(
                f"{channelName} {len(channel.getAllUsers())} :{channel.topic}"
            )

        client.handler.send(":End of LIST")

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.8
    def _handleKick(self, client: Client, message: Message):
        try:
            self._requireParams(client, message, 2)

            channelNames = message.params[0].split(",")
            nicks = message.params[1].split(",")
            try:
                reason = " ".join(message.params[2:]).lstrip(":")
            except IndexError:
                reason = None

            if len(channelNames) == 1:
                channel = self.channels[channelNames[0]]
                if channel.isOperator(client.user) or client.user.isOperator:
                    for nick in nicks:
                        user = self._getUserFromNick(nick)
                        if user and user.username in channel.users:
                            msg = f"KICK {channel.name} {nick}"
                            if reason:
                                msg += f" {reason}"
                            self._sendToChannel(client, channel, msg)
                            channel.removeUser(user)
            elif len(channelNames) == len(nicks):
                isOperator = False
                for channelName in channelNames:
                    channel = self.channels[channelName]
                    isOperator = (
                        channel.isOperator(client.user)
                        or client.user.isOperator
                    )
                if isOperator:
                    for channelName in channelNames:
                        channel = self.channels[channelName]
                        for nick in nicks:
                            user = self._getUserFromNick(nick)
                            if user and user.username in channel.users:
                                msg = f"KICK {channel.name} {nick}"
                                if reason:
                                    msg += f" {reason}"
                                self._sendToChannel(client, channel, msg)
                                channel.removeUser(user)
                else:
                    # TODO: ERR_CHANOPRIVSNEEDED
                    pass
            else:
                pass
        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.3.1
    def _handlePrivMsg(self, client: Client, message: Message):
        try:
            self._requireParams(client, message, 2)

            target = message.params[0]
            text = " ".join(message.params[1:]).lstrip(":")

            if target in self.channels:
                channel = self.channels[target]
                msg = f"PRIVMSG {channel.name} :{text}"
                self._sendToChannel(client, channel, msg, True)

        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.7.2
    def _handlePing(self, client: Client):
        client.handler.send("PONG")

    # https://datatracker.ietf.org/doc/html/rfc2813#section-5.2.1
    def _sendWelcome(self, client: Client) -> None:
        assert client.user.username is not None
        replies = [
            Reply.welcome(
                client.user.nick,
                client.user.username,
                client.handler.getHost(),
            ),
            Reply.yourHost(self.host, "0.0.1"),
            Reply.created(self.createdDate),
            Reply.myInfo(
                client.handler.getHost(),
                "0.0.1",
                "aiwroOs",
                "OovaimnqpsrtklbeI",
            ),
        ]
        for reply in replies:
            self._replyNumeric(client, reply)
        self._sendLUsers(client)
        self._sendMotd(client)

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.4.1
    def _sendMotd(self, client: Client) -> None:
        self._replyNumeric(client, Reply.motdStart(self.host))
        if self.motd:
            for line in self.motd:
                self._replyNumeric(client, Reply.motd(line))
        self._replyNumeric(client, Reply.endOfMotd())

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
            self._replyNumeric(client, reply)

    def _sendToChannel(
        self,
        sender: Client,
        channel: Channel,
        message: str,
        excludeSender: bool = False,
    ) -> None:
        for username in channel.getAllUsers():
            client = self.clients[username]
            if excludeSender and client == sender:
                continue

            client.handler.send(
                f":{self._getClientIdentifier(sender)} {message}"
            )

    # TODO: Make decorator?
    def _requireParams(
        self, client: Client, message: Message, paramCount: int = 1
    ) -> None:
        if (not message.params) or (len(message.params) < paramCount):
            self._replyNumeric(client, Reply.needMoreParams(message.command))
            raise FailedParamValidation(message.command)

    def _replyNumeric(self, client: Client, reply: Reply.Reply):
        message = (
            f"{self._getPrefix()}"
            f" {reply.code}"
            f" {client.user.username}"
            f" {reply.text}"
        )
        client.handler.send(message)

    def _userAlreadyRegistered(self, user: User) -> bool:
        return user.password is not None

    def _getPrefix(self) -> str:
        return f":{self.host}"

    def _getClientIdentifier(self, client: Client) -> str:
        return f"{client.user.nick}!{client.user.username}@{self.host}"


def getAnonymousIdentifier(handler: ClientHandler) -> str:
    return f"{handler.getHost()}:{handler.getPort()}"
