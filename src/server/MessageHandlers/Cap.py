from .Handler import Handler

from lib.Message import Message


# https://ircv3.net/specs/extensions/capability-negotiation
class Cap(Handler):
    def handle(self, message: Message):
        self.client.handler.send("CAP * LS :\r\n")
