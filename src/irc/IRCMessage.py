from .IRCUser import IRCUser


# https://datatracker.ietf.org/doc/html/rfc1459#section-2.3
class IRCMessage:
    """An IRC message"""

    rawMessage: str
    prefix: str
    command: str
    params: list[str]

    user: IRCUser

    def __init__(self, rawMessage, user):
        self.rawMessage = rawMessage
        self.user = user

        self.parseRawMessage()

    def parseRawMessage(self):
        """Parse the raw message into the IRCMessage object"""
        messageParts = self.rawMessage.split(" ")

        # The first part of the message is the prefix
        if messageParts[0].startswith(":"):
            self.prefix = messageParts[0][1:]
            self.command = messageParts[1]
            self.params = messageParts[2:]
        else:
            self.prefix = None
            self.command = messageParts[0]
            self.params = messageParts[1:]
