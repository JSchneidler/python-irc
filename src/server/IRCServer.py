from socketserver import ThreadingTCPServer
from threading import Lock
from typing import Optional
from datetime import datetime

from dataclasses import dataclass
from bcrypt import checkpw

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


@dataclass
class Client:
    handler: ClientHandler
    user: User

    def getIdentifier(self) -> str:
        return (
            f"{self.user.nick}!{self.user.username}@{self.handler.getHost()}"
        )


Clients = dict[str, Client]


@dataclass
class OperatorCredential:
    userHash: bytes
    passwordHash: bytes


OperatorCredentials = list[OperatorCredential]


class Server(ThreadingTCPServer):
    host: str
    port: int
    started: bool

    motd: list[str]
    createdDate: str
    channels: Channels
    clients: Clients
    newClients: Clients
    operatorCredentials: OperatorCredentials
    usersDisabled: bool

    lock: Lock

    def __init__(
        self,
        host: str,
        port: int,
        motd: list[str] = [],
        createdDate: str = datetime.now().isoformat(),
        operatorCredentials: OperatorCredentials = [],
    ) -> None:
        super().__init__((host, port), ClientHandler)
        self.started = False
        self.channels = {}
        self.clients = {}
        self.newClients = {}
        self.usersDisabled = False
        self.lock = Lock()

        self.daemon_threads = True
        self.block_on_close = False

        self.host = self.server_address[0]
        self.port = self.server_address[1]
        self.motd = motd
        self.createdDate = createdDate
        self.operatorCredentials = operatorCredentials

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

    def handleMessage(self, handler: ClientHandler, rawMessage: str) -> None:
        with self.lock:
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
            elif message.command == "OPER":
                self._handleOper(client, message)
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
            elif message.command == "USERHOST":
                self._handleUserHost(client, message)
            elif message.command == "TIME":
                self._handleTime(client)
            elif message.command == "PING":
                self._handlePing(client)
            elif message.command == "USERS":
                self._handleUsers(client)
            elif message.command == "MOTD":
                self._sendMotd(client)
            elif message.command == "LUSERS":
                self._sendLUsers(client)
            elif message.command == "ERROR":
                log.debug(f"Unhandled command: {message.rawMessage}")
            else:
                log.debug(f"Unhandled command: {message.rawMessage}")

    def _getClient(self, handler: ClientHandler) -> Client:
        if handler.user and handler.user.username:
            return self.clients[handler.user.username]
        else:
            return self.newClients[_getAnonymousIdentifier(handler)]

    def _getClientFromNick(self, nick: str) -> Client:
        return next(c for c in self.clients.values() if c.user.nick == nick)

    def _getUserFromNick(self, nick: str) -> User:
        return self._getClientFromNick(nick).user

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
                otherClients = list(
                    filter(
                        lambda c: c != client,
                        (self.clients | self.newClients).values(),
                    )
                )
                next(c for c in otherClients if c.user.nick == nick)
                self._replyNumeric(client, Reply.nickInUse(nick))
            except StopIteration:
                log.info(f"Changing nick from {client.user.nick} to {nick}")
                client.user.setNick(nick)

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.3
    def _handleUser(self, client: Client, message: Message) -> None:
        try:
            self._requireParams(client, message, 4)
            if client.user.username:
                self._replyNumeric(client, Reply.alreadyRegistered())
            else:
                client.user.username = message.params[0]
                invisibleMode = int(message.params[1]) & 4
                if invisibleMode:
                    client.user.setInvisible(True)
                client.user.realname = " ".join(message.params[3:])

                self.clients[client.user.username] = client
                del self.newClients[_getAnonymousIdentifier(client.handler)]
                self._sendWelcome(client)

                log.info(
                    (
                        f"Registered user {client.user.nick}"
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
                        log.info(f"{client.user.nick} is leaving all channels")
                        self._part(client, channel)
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
                        log.info(f"{client.user.nick} joined {channelName}")
                    else:
                        channel = Channel(channelName, client.user, key)
                        self.channels[channelName] = channel
                        log.info(f"{client.user.nick} created {channelName}")
                    self._sendToChannel(client, channel, f"JOIN {channelName}")
                    self._replyNumeric(client, Reply.topic(channel))
                    self._replyNumeric(client, Reply.names(channel))
                    self._replyNumeric(client, Reply.endOfNames(channelName))
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
                    self._part(client, channel, partMessage)
        except FailedParamValidation:
            pass

    def _part(
        self, client: Client, channel: Channel, partMessage: str = None
    ) -> None:
        message = f"PART {channel.name}"
        if partMessage:
            message += f" :{partMessage}"
        log.info(f"{client.user.nick} left {channel.name}")
        self._sendToChannel(client, channel, message)
        channel.removeUser(client.user)
        if len(channel.getAllUsers()) == 0:
            log.info(f"Deleting channel {channel.name}")
            del self.channels[channel.name]

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.4
    def _handleOper(self, client: Client, message: Message) -> None:
        try:
            self._requireParams(client, message, 2)

            user = message.params[0]
            password = message.params[1]

            for credential in self.operatorCredentials:
                if checkpw(user.encode(), credential.userHash) and checkpw(
                    password.encode(), credential.passwordHash
                ):
                    client.user.setOperator(True)
                    self._replyNumeric(client, Reply.youreOper())
                    return

            self._replyNumeric(client, Reply.passwordMismatch())

        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.3
    def _handleMode(self, client: Client, message: Message) -> None:
        try:
            self._requireParams(client, message)

            nickOrChannel = message.params[0]
            try:
                mode = message.params[1]
            except IndexError:
                mode = None

            if nickOrChannel in self.clients:
                self._userMode(client, nickOrChannel, mode)
            elif nickOrChannel in self.channels:
                channel = self.channels[nickOrChannel]
                self._channelMode(client, channel, mode)

        except FailedParamValidation:
            pass

    def _userMode(
        self, client: Client, nick: str, mode: Optional[str]
    ) -> None:
        if not mode:
            self._replyNumeric(
                client, Reply.userModeIs(client.user.getModes())
            )
        elif not _validUserMode(mode):
            self._replyNumeric(client, Reply.unknownModeFlag())
        elif nick == client.user.nick:
            self._setUserMode(client.user, mode)
        else:
            self._replyNumeric(client, Reply.usersDontMatch())

    def _setUserMode(self, user: User, mode: str) -> None:
        addMode = False
        if mode[0] == "+":
            addMode = True

        mode = mode[1]
        if mode == "a":
            user.setAway(addMode)
        elif mode == "i":
            user.setInvisible(addMode)
        elif mode == "o":
            user.setOperator(addMode)

    def _channelMode(
        self, client: Client, channel: Channel, mode: Optional[str]
    ) -> None:
        if not mode:
            self._replyNumeric(client, Reply.channelModeIs(channel))
        elif not _validChannelMode(mode):
            self._replyNumeric(client, Reply.unknownMode(channel, mode))
        else:
            self._setChannelMode(channel, mode)

    def _setChannelMode(self, channel: Channel, mode: str) -> None:
        addMode = False
        if mode[0] == "+":
            addMode = True

        mode = mode[1]
        try:
            modeParam = mode[2]
        except IndexError:
            modeParam = None

        if mode == "a":
            channel.setAnonymous(addMode)
        elif mode == "i":
            channel.setInviteOnly(addMode)
        elif mode == "m":
            channel.setModerated(addMode)
        elif mode == "t":
            channel.setTopicRestrict(addMode)
        elif mode == "l":
            if addMode:
                assert modeParam is not None
                channel.setUserLimit(int(modeParam))
            else:
                channel.removeUserLimit()
        elif mode == "k":
            if addMode:
                assert modeParam is not None
                channel.setKey(modeParam)
            else:
                channel.removeKey()
        elif mode == "o":
            assert modeParam is not None
            user = self._getUserFromNick(modeParam)
            if addMode:
                channel.addOperator(user)
            else:
                channel.removeOperator(user)

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
            self._replyNumeric(client, Reply.channelList(channel))
        self._replyNumeric(client, Reply.channelListEnd())

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
                if channel.isOperator(client.user) or client.user.isOperator():
                    for nick in nicks:
                        user = self._getUserFromNick(nick)
                        if user and user.username in channel.users:
                            self._kick(client, user, channel, reason)
            elif len(channelNames) == len(nicks):
                isOperator = False
                for channelName in channelNames:
                    channel = self.channels[channelName]
                    isOperator = (
                        channel.isOperator(client.user)
                        or client.user.isOperator()
                    )
                if isOperator:
                    for channelName in channelNames:
                        channel = self.channels[channelName]
                        for nick in nicks:
                            user = self._getUserFromNick(nick)
                            if user and user.username in channel.users:
                                self._kick(client, user, channel, reason)
                else:
                    # TODO: ERR_CHANOPRIVSNEEDED
                    pass
            else:
                pass
        except FailedParamValidation:
            pass

    def _kick(
        self,
        client: Client,
        kickedUser: User,
        channel: Channel,
        reason: str = None,
    ) -> None:
        message = f"KICK {channel.name} {kickedUser.nick}"
        if reason:
            message += f" :{reason}"
        self._sendToChannel(client, channel, message)
        channel.removeUser(kickedUser)

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.3.1
    def _handlePrivMsg(self, client: Client, message: Message):
        try:
            # TODO: Use ERR_NORECIPIENT and ERR_NOTEXTTOSEND instead?
            self._requireParams(client, message, 2)

            target = message.params[0]
            text = " ".join(message.params[1:]).lstrip(":")

            if target in self.channels:
                channel = self.channels[target]
                msg = f"PRIVMSG {channel.name} :{text}"
                self._sendToChannel(client, channel, msg, True)
            elif target in self.clients:
                toClient = self.clients[target]
                msg = f"PRIVMSG {toClient.user.nick} :{text}"
                toClient.handler.send(f":{client.getIdentifier()} {msg}")
            else:
                self._replyNumeric(client, Reply.noSuchNick(target))
        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-4.8
    def _handleUserHost(self, client: Client, message: Message):
        try:
            self._requireParams(client, message)

            nick = message.params[0]
            otherClient = self._getClientFromNick(nick)
            self._replyNumeric(
                client,
                Reply.userHost(otherClient.user, otherClient.getIdentifier()),
            )
        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.4.6
    def _handleTime(self, client: Client):
        self._replyNumeric(
            client, Reply.time(self._getPrefix(), datetime.now().isoformat())
        )

    # https://datatracker.ietf.org/doc/html/rfc2812#section-3.7.2
    def _handlePing(self, client: Client):
        client.handler.send("PONG")

    # https://datatracker.ietf.org/doc/html/rfc2812#section-4.6
    def _handleUsers(self, client: Client):
        if self.usersDisabled:
            self._replyNumeric(client, Reply.usersDisabled())
            return

        self._replyNumeric(client, Reply.usersStart())
        if len(self.clients) == 0:
            self._replyNumeric(client, Reply.noUsers())
        else:
            for client in self.clients.values():
                self._replyNumeric(
                    client, Reply.users(client.user, client.getIdentifier())
                )
        self._replyNumeric(client, Reply.endOfUsers())

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
        operators = filter(
            lambda c: c.user.isOperator(), self.clients.values()
        )
        replies = [
            Reply.lUserClient(len(self.clients), 0),
            Reply.lUserOp(len(list(operators))),
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

            client.handler.send(f":{sender.getIdentifier()} {message}")

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
            f" {client.user.nick}"
            f" {reply.text}"
        )
        client.handler.send(message)

    def _userAlreadyRegistered(self, user: User) -> bool:
        return user.password is not None

    def _getPrefix(self) -> str:
        return f":{self.host}"


def _getAnonymousIdentifier(handler: ClientHandler) -> str:
    return f"{handler.getHost()}:{handler.getPort()}"


def _validUserMode(mode: str) -> bool:
    return mode[0] in "+-" and mode[1] in "aio"


def _validChannelMode(mode: str) -> bool:
    return mode[0] in "+-" and mode[1] in "aimtkl"
