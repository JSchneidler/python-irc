from lib.Message import Message

from .Handler import Handler, FailedParamValidation
from .Reply import noSuchNick


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.3.1
class PrivMsg(Handler):
    def handle(self, message: Message):
        try:
            # TODO: Use ERR_NORECIPIENT and ERR_NOTEXTTOSEND instead?
            self._requireParams(self.client, message, 2)

            target = message.params[0]
            text = " ".join(message.params[1:]).lstrip(":")

            if target in self.serverState.channels:
                channel = self.serverState.channels[target]
                msg = f"PRIVMSG {channel.name} :{text}"
                self._sendToChannel(self.client, channel, msg, True)
            elif target in self.serverState.clients:
                toClient = self.serverState.clients[target]
                msg = f"PRIVMSG {toClient.user.nick} :{text}"
                toClient.handler.send(f":{self.client.getIdentifier()} {msg}\r\n")
            else:
                self._replyNumeric(self.client, noSuchNick(target))
        except FailedParamValidation:
            pass
