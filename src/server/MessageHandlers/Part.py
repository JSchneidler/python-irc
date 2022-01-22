from typing import Optional

from lib.logger import logger
from lib.Message import Message
from lib.Channel import Channel

from .Handler import Handler, FailedParamValidation
from ..ServerState import Client


log = logger.getChild("server.MessageHandlers.Part")


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.2
class Part(Handler):
    def handle(self, message: Message):
        try:
            self._requireParams(self.client, message)

            channels = message.params[0].split(",")
            try:
                partMessage = message.params[1].lstrip(":")
            except IndexError:
                partMessage = None

            for channelName in channels:
                if channelName in self.serverState.channels:
                    channel = self.serverState.channels[channelName]
                    self.part(self.client, channel, partMessage)
        except FailedParamValidation:
            pass

    def part(
        self,
        client: Client,
        channel: Channel,
        partMessage: Optional[str] = None,
    ) -> None:
        message = f"PART {channel.name}"
        if partMessage:
            message += f" :{partMessage}"
        log.info(f"{client.user.nick} left {channel.name}")
        self._sendToChannel(client, channel, message)
        channel.removeUser(client.user)
        if len(channel.getAllUsers()) == 0:
            log.info(f"Deleting channel {channel.name}")
            del self.serverState.channels[channel.name]
