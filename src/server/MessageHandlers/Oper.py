from bcrypt import checkpw

from lib.Message import Message

from .Handler import Handler, FailedParamValidation
from .Reply import youreOper, passwordMismatch


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.4
class Oper(Handler):
    def handle(self, message: Message):
        try:
            self._requireParams(self.client, message, 2)

            user = message.params[0]
            password = message.params[1]

            for credential in self.serverState.operatorCredentials:
                if checkpw(user.encode(), credential.userHash) and checkpw(
                    password.encode(), credential.passwordHash
                ):
                    self.client.user.setOperator(True)
                    self._replyNumeric(self.client, youreOper())
                    return

            self._replyNumeric(self.client, passwordMismatch())

        except FailedParamValidation:
            pass
