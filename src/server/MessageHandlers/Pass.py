from lib.Message import Message

from .Handler import Handler, FailedParamValidation
from .Reply import alreadyRegistered


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.1
class Pass(Handler):
    def handle(self, message: Message):
        try:
            self._requireParams(self.client, message)
            if self.serverState.userAlreadyRegistered(self.client.user):
                self._replyNumeric(self.client, alreadyRegistered())
            else:
                self.client.user.password = message.params[0]
        except FailedParamValidation:
            pass
