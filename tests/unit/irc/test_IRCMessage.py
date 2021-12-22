from irc.IRCMessage import Message


def test_Message():
    message = Message("QUIT", None)
    assert message.prefix is None
    assert message.command == "QUIT"
    assert message.params == []
