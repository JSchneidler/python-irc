from irc.IRCMessage import IRCMessage


def test_IRCMessage():
    message = IRCMessage("QUIT", None)
    assert message.prefix is None
    assert message.command == "QUIT"
    assert message.params == []
