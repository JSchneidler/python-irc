def needMoreParams(command: str) -> str:
    return f"461 {command} :Not enough parameters"


def alreadyRegistered() -> str:
    return "462 :Unauthorized command (already registered)"


def noNickGiven() -> str:
    return "431 :No nickname given"


def nickInUse(nick: str) -> str:
    return f"433 {nick} :Nickname is already in use"


def erroneusNick(nick: str) -> str:
    return f"432 {nick} :Erroneous nickname"


def motdStart(server: str) -> str:
    return f"375 :- {server} Message of the day - "


def motd(text: str) -> str:
    return f"372 :- {text}"


def endOfMotd() -> str:
    return "376 :End of MOTD command"


def lUserClient(users: int, services: int) -> str:
    return f"251 :There are {users} users and {services} services on 1 server"


def lUserOp(ops: int) -> str:
    return f"252 {ops} :operator(s) online"


def lUserUnknown(unknown: int) -> str:
    return f"253 {unknown} :unknown connection(s)"


def lUserChannels(channels: int) -> str:
    return f"254 {channels} :channels formed"


def lUserMe(me: int) -> str:
    return f"255 :I have {me} clients and 0 servers"
