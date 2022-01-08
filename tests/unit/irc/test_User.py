from pytest import raises

from irc.IRCUser import User


def test_User():
    user = User()

    assert user.nick == "*"


def test_User_setNick():
    user = User()
    user.setNick("test")

    assert user.nick == "test"

    user = User()
    with raises(ValueError):
        user.setNick("t" * 10)
    assert user.nick == "*"


def test_User_modes():
    user = User()

    assert user.getModes() == ""
    assert not user.isOperator()
    assert not user.isAway()
    assert not user.isInvisible()

    user.setAway(True)
    assert user.getModes() == "a"
    assert user.isAway()

    user.setInvisible(True)
    assert user.getModes() == "ai"
    assert user.isInvisible()

    user.setOperator(True)
    assert user.getModes() == "aio"
    assert user.isOperator()

    user.setAway(False)
    assert user.getModes() == "io"
    assert not user.isAway()

    user.setInvisible(False)
    assert user.getModes() == "o"
    assert not user.isInvisible()

    user.setOperator(False)
    assert user.getModes() == ""
    assert not user.isOperator()
