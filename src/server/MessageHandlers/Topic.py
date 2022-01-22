from lib.logger import logger
from lib.Message import Message

from .Handler import Handler, FailedParamValidation
from .Reply import topic


log = logger.getChild("server.MessageHandlers.Topic")


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.4
class Topic(Handler):
    def handle(self, message: Message):
        try:
            self._requireParams(self.client, message)

            channelName = message.params[0]
            try:
                newTopic = " ".join(message.params[1:]).lstrip(":")
            except IndexError:
                newTopic = None

            if channelName in self.serverState.channels:
                channel = self.serverState.channels[channelName]
                if newTopic:
                    channel.setTopic(newTopic)
                    self.client.handler.send(
                        (
                            f":{self.client.user.nick}"
                            f" TOPIC {channel.name}"
                            f" :{channel.topic}\r\n"
                        )
                    )
                    log.info(
                        (
                            f"User {self.client.user.nick}"
                            f" changed topic of channel {channel.name}"
                            f" to {channel.topic}"
                        )
                    )
                else:
                    self._replyNumeric(self.client, topic(channel))
            else:
                # TODO: ERR_NOTONCHANNEL?
                pass
        except FailedParamValidation:
            pass
