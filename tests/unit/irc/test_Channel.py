from pytest import raises

from irc.IRCChannel import (
    Channel,
    ChannelNameTooLong,
    MAX_CHANNEL_NAME_LENGTH,
    InvalidChannelPrefix,
    NoUserInChannel,
    NoUsername,
    UserAlreadyInChannel,
)
from irc.IRCUser import User


def createChannel():
    creator = User()
    creator.username = "test"
    channel = Channel("#test", creator)
    return channel


def test_Channel_name():
    user = User()
    user.username = "test2"

    # Valid prefixes
    Channel("&test", user)
    Channel("#test", user)
    Channel("+test", user)
    Channel("!test", user)

    with raises(ChannelNameTooLong):
        Channel("#" + "a" * (MAX_CHANNEL_NAME_LENGTH + 1), User())

    with raises(InvalidChannelPrefix):
        Channel("test", user)
        Channel("%test", user)
        Channel("3test", user)
        Channel(" test", user)
        Channel("_test", user)


def test_Channel_creator():
    creator = User()
    creator.username = "test"
    channel = Channel("#test", creator)

    assert len(channel.getAllUsers()) == 1
    assert len(channel.getOperators()) == 1
    assert len(channel.getUsers()) == 0
    assert channel.isOperator(creator)
    assert channel.getSimpleModes() == ""


def test_Channel_modes():
    channel = createChannel()

    channel.setAnonymous(True)
    assert channel.getSimpleModes() == "a"

    channel.setInviteOnly(True)
    assert channel.getSimpleModes() == "ai"

    channel.setModerated(True)
    assert channel.getSimpleModes() == "aim"

    channel.setTopicRestrict(True)
    assert channel.getSimpleModes() == "aimt"

    channel.setUserLimit(10)
    assert channel.getSimpleModes() == "aimtl"

    channel.setKey("key")
    assert channel.getSimpleModes() == "aimtlk"

    channel.setAnonymous(False)
    assert channel.getSimpleModes() == "imtlk"

    channel.setInviteOnly(False)
    assert channel.getSimpleModes() == "mtlk"

    channel.setModerated(False)
    assert channel.getSimpleModes() == "tlk"

    channel.setTopicRestrict(False)
    assert channel.getSimpleModes() == "lk"

    channel.removeUserLimit()
    assert channel.getSimpleModes() == "k"

    channel.removeKey()
    assert channel.getSimpleModes() == ""


def test_Channel_addRemoveUsers():
    channel = createChannel()

    user = User()
    user.username = "test2"

    channel.addUser(user)
    assert len(channel.getAllUsers()) == 2
    assert len(channel.getUsers()) == 1
    assert len(channel.getOperators()) == 1

    with raises(UserAlreadyInChannel):
        channel.addUser(user)

    channel.removeUser(user)
    assert len(channel.getAllUsers()) == 1
    assert len(channel.getUsers()) == 0
    assert len(channel.getOperators()) == 1

    with raises(NoUserInChannel):
        channel.removeUser(user)

    with raises(NoUsername):
        channel.addUser(User())


def test_Channel_addRemoveOperators():
    channel = createChannel()

    user = User()
    user.username = "test2"

    channel.addOperator(user)
    assert len(channel.getAllUsers()) == 2
    assert len(channel.getUsers()) == 0
    assert len(channel.getOperators()) == 2
    assert channel.isOperator(user)

    with raises(UserAlreadyInChannel):
        channel.addOperator(user)

    channel.removeOperator(user)
    assert len(channel.getAllUsers()) == 1
    assert len(channel.getUsers()) == 0
    assert len(channel.getOperators()) == 1
    assert not channel.isOperator(user)

    with raises(NoUserInChannel):
        channel.removeOperator(user)

    with raises(NoUsername):
        channel.addOperator(User())


def test_Channel_topic():
    channel = createChannel()

    assert channel.topic is None
    channel.setTopic("topic")
    assert channel.topic == "topic"
