from lib.Message import Message

from .Handler import Handler


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.7.2
class Ping(Handler):
    def handle(self, message: Message):
        self.client.handler.send("PONG\r\n")
