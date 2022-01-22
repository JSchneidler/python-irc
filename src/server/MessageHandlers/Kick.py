from typing import Optional

from lib.Message import Message
from lib.Channel import Channel
from lib.User import User

from .Handler import Handler, FailedParamValidation
from ..ServerState import Client


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.8
class Kick(Handler):
    def handle(self, message: Message):
        try:
            self._requireParams(self.client, message, 2)

            channelNames = message.params[0].split(",")
            nicks = message.params[1].split(",")
            try:
                reason = " ".join(message.params[2:]).lstrip(":")
            except IndexError:
                reason = None

            if len(channelNames) == 1:
                channel = self.serverState.channels[channelNames[0]]
                if (
                    channel.isOperator(self.client.user)
                    or self.client.user.isOperator()
                ):
                    for nick in nicks:
                        user = self.serverState.getUserFromNick(nick)
                        if user and user.username in channel.users:
                            self.kick(self.client, user, channel, reason)
            elif len(channelNames) == len(nicks):
                isOperator = False
                for channelName in channelNames:
                    channel = self.serverState.channels[channelName]
                    isOperator = (
                        channel.isOperator(self.client.user)
                        or self.client.user.isOperator()
                    )
                if isOperator:
                    for channelName in channelNames:
                        channel = self.serverState.channels[channelName]
                        for nick in nicks:
                            user = self.serverState.getUserFromNick(nick)
                            if user and user.username in channel.users:
                                self.kick(self.client, user, channel, reason)
                else:
                    # TODO: ERR_CHANOPRIVSNEEDED
                    pass
            else:
                pass
        except FailedParamValidation:
            pass

    def kick(
        self,
        client: Client,
        kickedUser: User,
        channel: Channel,
        reason: Optional[str] = None,
    ) -> None:
        message = f"KICK {channel.name} {kickedUser.nick}"
        if reason:
            message += f" :{reason}"
        self._sendToChannel(client, channel, message)
        channel.removeUser(kickedUser)
