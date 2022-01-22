from lib.logger import logger
from lib.Message import Message

from .Handler import Handler, FailedParamValidation
from .LUsers import LUsers
from .Motd import Motd
from ..ServerState import Client
from .Reply import alreadyRegistered, welcome, yourHost, created, myInfo


log = logger.getChild("server.MessageHandlers.User")


# https://datatracker.ietf.org/doc/html/rfc2812#section-3.1.3
class User(Handler):
    def handle(self, message: Message):
        try:
            self._requireParams(self.client, message, 4)
            if self.client.user.username:
                self._replyNumeric(self.client, alreadyRegistered())
            else:
                self.serverState.removeUser(self.client.handler)

                self.client.user.username = message.params[0]
                invisibleMode = int(message.params[1]) & 4
                if invisibleMode:
                    self.client.user.setInvisible(True)
                self.client.user.realname = " ".join(message.params[3:])

                self.serverState.clients[self.client.user.username] = self.client
                self.sendWelcome(self.client)

                log.info(
                    (
                        f"Registered user {self.client.user.nick}"
                        f" from {self.client.handler.getClientAddress()}"
                    )
                )
        except FailedParamValidation:
            pass

    # https://datatracker.ietf.org/doc/html/rfc2813#section-5.2.1
    def sendWelcome(self, client: Client) -> None:
        assert client.user.username is not None
        replies = [
            welcome(
                client.user.nick,
                client.user.username,
                client.handler.getHost(),
            ),
            yourHost(self.serverState.host, "0.0.1"),
            created(self.serverState.createdDate),
            myInfo(
                client.handler.getHost(),
                "0.0.1",
                "aiwroOs",
                "OovaimnqpsrtklbeI",
            ),
            *LUsers(self.serverState, self.client).lUsers(),
            *Motd(self.serverState, self.client).motd(),
        ]
        self._replyNumeric(client, replies)
