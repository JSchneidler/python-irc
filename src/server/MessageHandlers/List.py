from lib.Message import Message
from lib.Channel import Channels

from .Handler import Handler
from .Reply import Reply, channelList, channelListEnd


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.6
class List(Handler):
    def handle(self, message: Message):
        channels: list[str] | Channels
        try:
            channels = message.params[0].split(",")
        except IndexError:
            channels = self.serverState.channels

        replies: list[Reply] = []
        for channelName in channels:
            channel = self.serverState.channels[channelName]
            replies.append(channelList(channel))
        replies.append(channelListEnd())
        self._replyNumeric(self.client, replies)
