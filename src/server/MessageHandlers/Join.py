from lib.logger import logger
from lib.Message import Message
from lib.Channel import Channel

from .Handler import Handler, FailedParamValidation
from .Part import Part
from .Reply import badChannelKey, topic, names, endOfNames


log = logger.getChild("server.MessageHandlers.Join")


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.1
class Join(Handler):
    def handle(self, message: Message):
        try:
            self._requireParams(self.client, message)

            # Leave all channels
            if message.params[0] == "0":
                for channelName in self.serverState.channels:
                    channel = self.serverState.channels[channelName]
                    if self.client.user.username in channel.getAllUsers():
                        log.info(f"{self.client.user.nick} is leaving all channels")
                        Part(self.serverState, self.client).part(self.client, channel)
            else:
                channels = message.params[0].split(",")
                try:
                    keys = message.params[1].split(",")
                except IndexError:
                    keys = None

                for i, channelName in enumerate(channels):
                    key = None
                    if keys and len(keys) > i:
                        key = keys[i]

                    if channelName in self.serverState.channels:
                        channel = self.serverState.channels[channelName]
                        if channel.key and key != channel.key:
                            self._replyNumeric(self.client, badChannelKey(channelName))
                            break
                        channel.addUser(self.client.user)
                        log.info(f"{self.client.user.nick} joined {channelName}")
                    else:
                        channel = Channel(channelName, self.client.user, key)
                        self.serverState.channels[channelName] = channel
                        log.info(f"{self.client.user.nick} created {channelName}")
                    self._sendToChannel(self.client, channel, f"JOIN {channelName}")
                    replies = [
                        topic(channel),
                        names(channel),
                        endOfNames(channelName),
                    ]
                    self._replyNumeric(self.client, replies)
        except FailedParamValidation:
            pass
