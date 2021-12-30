from typing import Optional

from .logger import logger
from .IRCMessage import Messages
from .IRCUser import User, Users


MAX_CHANNEL_NAME_LENGTH = 50
VALID_CHANNEL_PREFIXES = ["&", "#", "+", "!"]


class ChannelNameTooLong(Exception):
    pass


class InvalidChannelPrefix(Exception):
    pass


class NoUsername(Exception):
    pass


class UserAlreadyInChannel(Exception):
    pass


log = logger.getChild("IRCChannel")


# https://datatracker.ietf.org/doc/html/rfc1459#section-1.3
class Channel:
    name: str
    key: Optional[str] = None
    topic: Optional[str] = None
    users: Users = {}
    operators: Users = {}
    messages: Messages = []

    def __init__(self, name: str, creator: User, key: str = None):
        if len(name) > MAX_CHANNEL_NAME_LENGTH:
            raise ChannelNameTooLong(f"Channel name too long: {name}")
        if not name[0] in VALID_CHANNEL_PREFIXES:
            raise InvalidChannelPrefix(f"Invalid channel prefix: {name}")

        self.name = name
        self.key = key
        self.addOperator(creator)

    def getUsers(self) -> Users:
        return self.users

    def getOperators(self) -> Users:
        return self.operators

    def getAllUsers(self) -> Users:
        return self.users | self.operators

    def isOperator(self, user: User) -> bool:
        return user.username in self.operators

    def setTopic(self, topic: str) -> None:
        self.topic = topic

    def addUser(self, user: User) -> None:
        if user.username in self.users:
            raise UserAlreadyInChannel()
        elif user.username:
            log.info(f"Adding user {user.username} to channel {self.name}")
            self.users[user.username] = user
        else:
            raise NoUsername(user)

    def addOperator(self, user: User) -> None:
        self.operators[user.username] = user

    def removeUser(self, user: User) -> None:
        if user.username in self.users:
            log.info(f"Removing user {user.username} from channel {self.name}")
            del self.users[user.username]


Channels = dict[str, Channel]
