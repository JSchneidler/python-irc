from typing import Optional

from lib.Message import Message
from lib.User import User
from lib.Channel import Channel

from .Handler import Handler, FailedParamValidation
from ..ServerState import Client
from .Reply import (
    userModeIs,
    unknownModeFlag,
    usersDontMatch,
    channelModeIs,
    unknownMode,
)


def _validUserMode(mode: str) -> bool:
    return mode[0] in "+-" and mode[1] in "aio"


def _validChannelMode(mode: str) -> bool:
    return mode[0] in "+-" and mode[1] in "aimtkl"


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.2.3
class Mode(Handler):
    def handle(self, message: Message):
        try:
            self._requireParams(self.client, message)

            nickOrChannel = message.params[0]
            try:
                mode = message.params[1]
            except IndexError:
                mode = None

            if nickOrChannel in self.serverState.clients:
                self.userMode(self.client, nickOrChannel, mode)
            elif nickOrChannel in self.serverState.channels:
                channel = self.serverState.channels[nickOrChannel]
                self.channelMode(self.client, channel, mode)

        except FailedParamValidation:
            pass

    def userMode(self, client: Client, nick: str, mode: Optional[str]) -> None:
        if not mode:
            self._replyNumeric(client, userModeIs(client.user.getModes()))
        elif not _validUserMode(mode):
            self._replyNumeric(client, unknownModeFlag())
        elif nick == client.user.nick:
            self.setUserMode(client.user, mode)
        else:
            self._replyNumeric(client, usersDontMatch())

    def setUserMode(self, user: User, mode: str) -> None:
        addMode = False
        if mode[0] == "+":
            addMode = True

        mode = mode[1]
        if mode == "a":
            user.setAway(addMode)
        elif mode == "i":
            user.setInvisible(addMode)
        elif mode == "o":
            user.setOperator(addMode)

    def channelMode(
        self, client: Client, channel: Channel, mode: Optional[str]
    ) -> None:
        if not mode:
            self._replyNumeric(client, channelModeIs(channel))
        elif not _validChannelMode(mode):
            self._replyNumeric(client, unknownMode(channel, mode))
        else:
            self.setChannelMode(channel, mode)

    def setChannelMode(self, channel: Channel, mode: str) -> None:
        addMode = False
        if mode[0] == "+":
            addMode = True

        mode = mode[1]
        try:
            modeParam = mode[2]
        except IndexError:
            modeParam = None

        if mode == "a":
            channel.setAnonymous(addMode)
        elif mode == "i":
            channel.setInviteOnly(addMode)
        elif mode == "m":
            channel.setModerated(addMode)
        elif mode == "t":
            channel.setTopicRestrict(addMode)
        elif mode == "l":
            if addMode:
                assert modeParam is not None
                channel.setUserLimit(int(modeParam))
            else:
                channel.removeUserLimit()
        elif mode == "k":
            if addMode:
                assert modeParam is not None
                channel.setKey(modeParam)
            else:
                channel.removeKey()
        elif mode == "o":
            assert modeParam is not None
            user = self.serverState.getUserFromNick(modeParam)
            if addMode:
                channel.addOperator(user)
            else:
                channel.removeOperator(user)
