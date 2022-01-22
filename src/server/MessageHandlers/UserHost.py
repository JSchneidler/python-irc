from lib.Message import Message

from .Handler import Handler, FailedParamValidation
from .Reply import userHost


# https://datatracker.ietf.org/doc/html/rfc2812#section-4.8
class UserHost(Handler):
    def handle(self, message: Message):
        try:
            self._requireParams(self.client, message)

            nick = message.params[0]
            otherClient = self.serverState.getClientFromNick(nick)
            self._replyNumeric(
                self.client,
                userHost(otherClient.user, otherClient.getIdentifier()),
            )
        except FailedParamValidation:
            pass
