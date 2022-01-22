from lib.Message import Message

from .Handler import Handler
from .Reply import Reply, lUserClient, lUserOp, lUserUnknown, lUserChannels, lUserMe


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.4.2
class LUsers(Handler):
    def handle(self, message: Message):
        self._replyNumeric(self.client, self.lUsers())

    def lUsers(self) -> list[Reply]:
        operators = filter(
            lambda c: c.user.isOperator(), self.serverState.clients.values()
        )
        return [
            lUserClient(len(self.serverState.clients), 0),
            lUserOp(len(list(operators))),
            lUserUnknown(len(self.serverState.newClients)),
            lUserChannels(len(self.serverState.channels)),
            lUserMe(len(self.serverState.clients)),
        ]
