MAX_NICK_LENGTH = 9


class User:
    password: str = None
    mode: int = None
    nick: str = None
    username: str = None
    realname: str = None
    isOperator: bool = None


Users = dict[str, User]
