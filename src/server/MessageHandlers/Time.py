from datetime import datetime

from lib.Message import Message

from .Handler import Handler
from .Reply import time


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.4.6
class Time(Handler):
    def handle(self, message: Message):
        self._replyNumeric(
            self.client, time(self.serverState.getPrefix(), datetime.now().isoformat())
        )
