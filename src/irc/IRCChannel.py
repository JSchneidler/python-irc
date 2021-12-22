from irc.IRCMessage import Message

from .IRCUser import User


MAX_CHANNEL_NAME_LENGTH = 200


# https://datatracker.ietf.org/doc/html/rfc1459#section-1.3
class Channel:
    name: str = None
    users: list[User] = []
    ops: list[User] = []
    messages: list[Message] = []


Channels = dict[str, Channel]
