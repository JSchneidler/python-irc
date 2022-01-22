from lib.Message import Message

from .Handler import Handler
from .Reply import Reply, motdStart, motd, endOfMotd


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.4.1
class Motd(Handler):
    def handle(self, message: Message):
        self._replyNumeric(self.client, self.motd())

    def motd(self) -> list[Reply]:
        replies = [motdStart(self.serverState.host)]
        if self.serverState.motd:
            for line in self.serverState.motd:
                replies.append(motd(line))
        replies.append(endOfMotd())
        return replies
