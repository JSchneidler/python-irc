from .IRCUser import User


# https://datatracker.ietf.org/doc/html/rfc1459#section-2.3
class Message:
    rawMessage: str = None
    prefix: str = None
    command: str = None
    params: list[str] = None

    user: User

    def __init__(self, rawMessage, user: User):
        self.rawMessage = rawMessage
        self.user = user

        self._parseRawMessage()

    def _parseRawMessage(self):
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
