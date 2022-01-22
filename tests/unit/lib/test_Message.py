from lib.Message import Message
from lib.User import User


def test_Message():
    message = Message("QUIT", User())
    assert message.prefix is None
    assert message.command == "QUIT"
    assert message.params == []
