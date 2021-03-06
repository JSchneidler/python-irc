from lib.User import User
from lib.Channel import Channel


class Reply:
    code: str
    text: str

    def __init__(self, code: str, text: str) -> None:
        self.code = code
        self.text = text


def welcome(nick: str, username: str, host: str) -> Reply:
    return Reply(
        "001",
        f":Welcome to the Internet Relay Network {nick}!{username}@{host}",
    )


def yourHost(serverName: str, version: str) -> Reply:
    return Reply("002", f":Your host is {serverName}, running version {version}")


def created(date: str) -> Reply:
    return Reply("003", f":This server was created {date}")


def myInfo(serverName: str, version: str, userModes: str, channelModes: str) -> Reply:
    return Reply("004", f":{serverName} {version} {userModes} {channelModes}")


def needMoreParams(command: str) -> Reply:
    return Reply("461", f"{command} :Not enough parameters")


def alreadyRegistered() -> Reply:
    return Reply("462", ":Unauthorized command (already registered)")


def noNickGiven() -> Reply:
    return Reply("431", ":No nickname given")


def nickInUse(nick: str) -> Reply:
    return Reply("433", f"{nick} :Nickname is already in use")


def erroneusNick(nick: str) -> Reply:
    return Reply("432", f"{nick} :Erroneous nickname")


def channelModeIs(channel: Channel) -> Reply:
    return Reply("324", f"{channel.name} {channel.getSimpleModes()}")


def motdStart(server: str) -> Reply:
    return Reply("375", f":- {server} Message of the day - ")


def motd(text: str) -> Reply:
    return Reply("372", f":- {text}")


def endOfMotd() -> Reply:
    return Reply("376", ":End of MOTD command")


def youreOper() -> Reply:
    return Reply("381", ":You are now an IRC operator")


def usersStart() -> Reply:
    return Reply("392", ":UserID   Terminal  Host")


def users(user: User, clientIdentifier: str) -> Reply:
    return Reply("393", f":{user.username} * {clientIdentifier}")


def endOfUsers() -> Reply:
    return Reply("394", ":End of users")


def noUsers() -> Reply:
    return Reply("395", ":Nobody logged in")


def userModeIs(mode: str) -> Reply:
    return Reply("221", mode)


def lUserClient(users: int, services: int) -> Reply:
    return Reply("251", f":There are {users} users and {services} services on 1 server")


def lUserOp(ops: int) -> Reply:
    return Reply("252", f"{ops} :operator(s) online")


def lUserUnknown(unknown: int) -> Reply:
    return Reply("253", f"{unknown} :unknown connection(s)")


def lUserChannels(channels: int) -> Reply:
    return Reply("254", f"{channels} :channels formed")


def lUserMe(me: int) -> Reply:
    return Reply("255", f":I have {me} clients and 0 servers")


def noSuchNick(nick: str) -> Reply:
    return Reply("401", f"{nick} :No such nick/channel")


def noSuchChannel(channelName: str) -> Reply:
    return Reply("403", f"{channelName} :No such channel")


def usersDisabled() -> Reply:
    return Reply("446", ":USERS has been disabled")


def passwordMismatch() -> Reply:
    return Reply("464", ":Password incorrect")


def badChannelKey(channelName: str) -> Reply:
    return Reply("475", f"{channelName} :Cannot join channel (+k)")


def userHost(user: User, clientIdentifier: str) -> Reply:
    isOperator = "*" if user.isOperator() else None
    isAway = "-" if user.isAway() else None

    return Reply(
        "302",
        f":{user.nick}{isOperator}={isAway}{clientIdentifier}",
    )


def channelList(channel: Channel) -> Reply:
    return Reply("322", f"{channel.name} {len(channel.getAllUsers())} :{channel.topic}")


def channelListEnd() -> Reply:
    return Reply("323", ":End of LIST")


def topic(channel: Channel) -> Reply:
    if channel.topic:
        return Reply("332", f"{channel.name} :{channel.topic}")
    else:
        return Reply("331", f"{channel.name} :No topic is set")


def names(channel: Channel) -> Reply:
    operators = list(map(lambda opName: f"@{opName}", channel.getOperators().keys()))
    users = list(channel.getUsers().keys())
    return Reply("353", f"= {channel.name} :{' '.join(operators + users)}")


def endOfNames(channelName: str) -> Reply:
    return Reply("366", f"{channelName} :End of NAMES list")


def time(server: str, time: str) -> Reply:
    return Reply("391", f"{server} :{time}")


def unknownMode(channel: Channel, mode: str) -> Reply:
    return Reply("472", f"{mode} :is unknown mode char to me for {channel.name}")


def noChannelModes(channelName: str) -> Reply:
    return Reply("477", f"{channelName} :Channel doesn't support modes")


def unknownModeFlag() -> Reply:
    return Reply("501", ":Unknown MODE flag")


def usersDontMatch() -> Reply:
    return Reply("502", ":Cannot change mode for other users")
