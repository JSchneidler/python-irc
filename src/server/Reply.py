from irc.IRCUser import User, Users


class Reply:
    code: str
    text: str

    def __init__(self, code: int, text: str) -> None:
        self.code = code
        self.text = text


def welcome(nick: str, username: str, host: str) -> Reply:
    return Reply(
        "001", f":Welcome to the Internet Relay Network\r\n{nick}!{username}@{host}"
    )


def yourHost(serverName: str, version: str) -> Reply:
    return Reply("002", f":Your host is {serverName}, running version {version}")


def created(date: str) -> Reply:
    return Reply("003", f":This server was created {date}")


def myInfo(serverName: str, version: str, userModes: str, channelModes: str) -> Reply:
    return Reply("004", f":{serverName} {version} {userModes} {channelModes}")


def needMoreParams(command: str) -> Reply:
    return Reply(461, f"{command} :Not enough parameters")


def alreadyRegistered() -> Reply:
    return Reply(462, ":Unauthorized command (already registered)")


def noNickGiven() -> Reply:
    return Reply(431, ":No nickname given")


def nickInUse(nick: str) -> Reply:
    return Reply(433, f"{nick} :Nickname is already in use")


def erroneusNick(nick: str) -> Reply:
    return Reply(432, f"{nick} :Erroneous nickname")


def motdStart(server: str) -> Reply:
    return Reply(375, f":- {server} Message of the day - ")


def motd(text: str) -> Reply:
    return Reply(372, f":- {text}")


def endOfMotd() -> Reply:
    return Reply(376, ":End of MOTD command")


def lUserClient(users: int, services: int) -> Reply:
    return Reply(251, f":There are {users} users and {services} services on 1 server")


def lUserOp(ops: int) -> Reply:
    return Reply(252, f"{ops} :operator(s) online")


def lUserUnknown(unknown: int) -> Reply:
    return Reply(253, f"{unknown} :unknown connection(s)")


def lUserChannels(channels: int) -> Reply:
    return Reply(254, f"{channels} :channels formed")


def lUserMe(me: int) -> Reply:
    return Reply(255, f":I have {me} clients and 0 servers")


def badChannelKey(channel: str) -> Reply:
    return Reply(475, f"{channel} :Cannot join channel (+k)")


def topic(channel: str, topic: str) -> str:
    if topic:
        return Reply(332, f"{channel} :{topic}").text
    else:
        return Reply(331, f"{channel} :No topic is set").text


def names(channel: str, user: User, users: Users) -> Reply:
    return Reply(353, f"{channel} = {user.nick} :{' '.join(users.keys())}")


def endOfNames(channel: str, user: User) -> Reply:
    return Reply(366, f"{user.nick} {channel} :End of NAMES list")
