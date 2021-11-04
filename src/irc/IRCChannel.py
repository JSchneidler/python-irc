from irc.IRCMessage import IRCMessage
from typing import Dict

from .IRCUser import IRCUser


MAX_CHANNEL_NAME_LENGTH = 200


# https://datatracker.ietf.org/doc/html/rfc1459#section-1.3
class IRCChannel:
    """Represents an IRC channel"""

    name: str
    users: list[IRCUser]
    ops: list[IRCUser]
    messages: list[IRCMessage]

    pass


Channels = Dict[str, IRCChannel]
