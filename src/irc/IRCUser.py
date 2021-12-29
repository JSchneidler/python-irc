from typing import Optional

MAX_NICK_LENGTH = 9


class User:
    password: Optional[str] = None
    mode: Optional[int] = None
    nick: Optional[str] = None
    username: Optional[str] = None
    realname: Optional[str] = None
    isOperator: bool = False


Users = dict[str, User]
