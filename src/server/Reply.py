class Reply:
    code: str
    text: str

    def __init__(self, code: int, text: str) -> None:
        self.code = code
        self.text = text


def welcome(nick: str, username: str, host: str) -> str:
    return Reply(
        "001",
        ":Welcome to the Internet Relay Network\r\n{}!{}@{}".format(
            nick, username, host
        ),
    )


def yourHost(serverName: str, version: str) -> str:
    return Reply(
        "002", ":Your host is {}, running version {}".format(serverName, version)
    )


def created(date: str) -> str:
    return Reply("003", ":This server was created {}".format(date))


def myInfo(serverName: str, version: str, userModes: str, channelModes: str) -> str:
    return Reply(
        "004", ":{} {} {} {}".format(serverName, version, userModes, channelModes)
    )


def needMoreParams(command: str) -> str:
    return Reply(461, f"{command} :Not enough parameters")


def alreadyRegistered() -> str:
    return Reply(462, ":Unauthorized command (already registered)")


def noNickGiven() -> str:
    return Reply(431, ":No nickname given")


def nickInUse(nick: str) -> str:
    return Reply(433, f"{nick} :Nickname is already in use")


def erroneusNick(nick: str) -> str:
    return Reply(432, f"{nick} :Erroneous nickname")


def motdStart(server: str) -> str:
    return Reply(375, f":- {server} Message of the day - ")


def motd(text: str) -> str:
    return Reply(372, f":- {text}")


def endOfMotd() -> str:
    return Reply(376, ":End of MOTD command")


def lUserClient(users: int, services: int) -> str:
    return Reply(251, f":There are {users} users and {services} services on 1 server")


def lUserOp(ops: int) -> str:
    return Reply(252, f"{ops} :operator(s) online")


def lUserUnknown(unknown: int) -> str:
    return Reply(253, f"{unknown} :unknown connection(s)")


def lUserChannels(channels: int) -> str:
    return Reply(254, f"{channels} :channels formed")


def lUserMe(me: int) -> str:
    return Reply(255, f":I have {me} clients and 0 servers")
