from lib.logger import logger
from lib.Message import Message

from .Handler import Handler
from .Reply import noNickGiven, nickInUse


log = logger.getChild("server.MessageHandlers.Nick")


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.2
class Nick(Handler):
    def handle(self, message: Message):
        if len(message.params) == 0:
            self._replyNumeric(self.client, noNickGiven())
        else:
            nick = message.params[0]
            try:
                otherClients = list(
                    filter(
                        lambda c: c != self.client,
                        (
                            self.serverState.clients | self.serverState.newClients
                        ).values(),
                    )
                )
                next(c for c in otherClients if c.user.nick == nick)
                self._replyNumeric(self.client, nickInUse(nick))
            except StopIteration:
                log.info(f"Changing nick from {self.client.user.nick} to {nick}")
                self.client.user.setNick(nick)
