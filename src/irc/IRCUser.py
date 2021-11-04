from typing import Dict

MAX_NICK_LENGTH = 9


class IRCUser:
    """Represents an IRC user"""

    nick: str
    isOperator: bool

    pass


Users = Dict[str, IRCUser]
