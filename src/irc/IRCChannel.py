from typing import Optional
import logging

from .IRCMessage import Messages
from .IRCUser import User, Users


MAX_CHANNEL_NAME_LENGTH = 50


class NoUsername(Exception):
    pass


class UserAlreadyInChannel(Exception):
    pass


# https://datatracker.ietf.org/doc/html/rfc1459#section-1.3
class Channel:
    name: str
    key: Optional[str]
    topic: Optional[str]
    users: Users = {}
    messages: Messages = []

    def __init__(self, name: str, key: str = None):
        self.name = name
        self.key = key

    def setTopic(self, topic: str) -> None:
        self.topic = topic

    def addUser(self, user: User) -> None:
        if user.username in self.users:
            raise UserAlreadyInChannel()
        elif user.username:
            logging.info(f"Adding user {user.username} to channel {self.name}")
            self.users[user.username] = user
        else:
            raise NoUsername(user)

    def removeUser(self, user: User) -> None:
        if user.username in self.users:
            logging.info(
                f"Removing user {user.username} from channel {self.name}"
            )
            del self.users[user.username]


Channels = dict[str, Channel]
