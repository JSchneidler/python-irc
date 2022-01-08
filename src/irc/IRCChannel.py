from dataclasses import dataclass
from typing import Optional

from .logger import logger
from .IRCMessage import Messages
from .IRCUser import User, Users


MAX_CHANNEL_NAME_LENGTH = 50
VALID_CHANNEL_PREFIXES = ["&", "#", "+", "!"]


@dataclass
class Modes:
    anonymous: bool = False
    inviteOnly: bool = False
    moderated: bool = False
    topic: bool = False
    userLimit: bool = False
    channelKey: bool = False


class ChannelNameTooLong(Exception):
    pass


class InvalidChannelPrefix(Exception):
    pass


class NoUsername(Exception):
    pass


class UserAlreadyInChannel(Exception):
    pass


class NoUserInChannel(Exception):
    pass


log = logger.getChild("IRCChannel")


# https://datatracker.ietf.org/doc/html/rfc1459#section-1.3
class Channel:
    name: str
    users: Users
    operators: Users
    messages: Messages
    modes: Modes
    topic: Optional[str]
    key: Optional[str]
    userLimit: Optional[int]

    def __init__(self, name: str, creator: User, key: str = None):
        if len(name) > MAX_CHANNEL_NAME_LENGTH:
            raise ChannelNameTooLong(f"Channel name too long: {name}")
        if not name[0] in VALID_CHANNEL_PREFIXES:
            raise InvalidChannelPrefix(f"Invalid channel prefix: {name}")

        self.users = {}
        self.operators = {}
        self.messages = []
        self.modes = Modes()
        self.topic = None
        self.key = None
        self.userLimit = None

        self.name = name
        self.addOperator(creator)
        if key:
            self.setKey(key)

    def getUsers(self) -> Users:
        return self.users

    def getOperators(self) -> Users:
        return self.operators

    def getAllUsers(self) -> Users:
        return self.users | self.operators

    def isOperator(self, user: User) -> bool:
        return user.username in self.operators

    def setKey(self, key: str) -> None:
        self.key = key
        self.modes.channelKey = True

    def removeKey(self) -> None:
        self.key = None
        self.modes.channelKey = False

    def setTopic(self, topic: str) -> None:
        self.topic = topic

    def addUser(self, user: User) -> None:
        if user.username in self.users:
            raise UserAlreadyInChannel()
        elif user.username:
            log.info(f"Adding user {user.nick} to channel {self.name}")
            self.users[user.username] = user
        else:
            raise NoUsername(user)

    def removeUser(self, user: User) -> None:
        if user.username in self.users:
            log.info(f"Removing user {user.nick} from channel {self.name}")
            del self.users[user.username]
        else:
            raise NoUserInChannel(user)

    def addOperator(self, user: User) -> None:
        if user.username in self.operators:
            raise UserAlreadyInChannel()
        elif user.username:
            log.info(f"Adding operator {user.nick} to channel {self.name}")
            self.operators[user.username] = user
        else:
            raise NoUsername(user)

    def removeOperator(self, user: User) -> None:
        if user.username in self.operators:
            log.info(f"Removing operator {user.nick} from channel {self.name}")
            del self.operators[user.username]
        else:
            raise NoUserInChannel(user)

    def setAnonymous(self, anonymous: bool) -> None:
        self.modes.anonymous = anonymous

    def setInviteOnly(self, inviteOnly: bool) -> None:
        self.modes.inviteOnly = inviteOnly

    def setModerated(self, moderated: bool) -> None:
        self.modes.moderated = moderated

    def setTopicRestrict(self, restrict: bool) -> None:
        self.modes.topic = restrict

    def setUserLimit(self, limit: int) -> None:
        self.userLimit = limit
        self.modes.userLimit = True

    def removeUserLimit(self) -> None:
        self.userLimit = None
        self.modes.userLimit = False

    def getSimpleModes(self) -> str:
        modes = ""
        if self.modes.anonymous:
            modes += "a"
        if self.modes.inviteOnly:
            modes += "i"
        if self.modes.moderated:
            modes += "m"
        if self.modes.topic:
            modes += "t"
        if self.modes.userLimit:
            modes += "l"
        if self.modes.channelKey:
            modes += "k"
        return modes


Channels = dict[str, Channel]
