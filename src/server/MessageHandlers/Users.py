from lib.Message import Message

from .Handler import Handler
from .Reply import Reply, usersDisabled, usersStart, noUsers, users, endOfUsers


# https://datatracker.ietf.org/doc/html/rfc2812#section-4.6
class Users(Handler):
    def handle(self, message: Message):
        if self.serverState.usersDisabled:
            self._replyNumeric(self.client, usersDisabled())
            return

        replies: list[Reply] = [usersStart()]
        if len(self.serverState.clients) == 0:
            replies.append(noUsers())
        else:
            for client in self.serverState.clients.values():
                replies.append(users(client.user, client.getIdentifier()))
        replies.append(endOfUsers())
        self._replyNumeric(self.client, replies)
