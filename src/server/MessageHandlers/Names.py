from lib.Message import Message

from .Handler import Handler
from .Reply import names


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.5
class Names(Handler):
    def handle(self, message: Message):
        channels = message.params[0].split(",")

        for channelName in channels:
            if channelName in self.serverState.channels:
                channel = self.serverState.channels[channelName]
                self._replyNumeric(self.client, names(channel))
