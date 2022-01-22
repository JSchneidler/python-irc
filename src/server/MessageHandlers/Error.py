from lib.logger import logger
from lib.Message import Message

from .Handler import Handler


log = logger.getChild("server.MessageHandlers.Error")


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.1
class Error(Handler):
    def handle(self, message: Message):
        log.debug(f"Unhandled command: {message.rawMessage}")
