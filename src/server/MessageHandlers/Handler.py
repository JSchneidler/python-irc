from abc import ABC, abstractmethod
from typing import overload

from lib.Message import Message
from lib.Channel import Channel

from ..ServerState import ServerState, Client
from . import Reply


class FailedParamValidation(Exception):
    pass


class Handler(ABC):
    serverState: ServerState
    client: Client

    def __init__(self, serverState: ServerState, client: Client):
        self.serverState = serverState
        self.client = client

    @abstractmethod
    def handle(self, message: Message):
        ...

    # TODO: Make decorator?
    def _requireParams(
        self, client: Client, message: Message, paramCount: int = 1
    ) -> None:
        if (not message.params) or (len(message.params) < paramCount):
            self._replyNumeric(client, Reply.needMoreParams(message.command))
            raise FailedParamValidation(message.command)

    @overload
    def _replyNumeric(self, client: Client, reply: Reply.Reply) -> None:
        ...

    @overload
    def _replyNumeric(self, client: Client, reply: list[Reply.Reply]) -> None:
        ...

    def _replyNumeric(
        self, client: Client, reply: Reply.Reply | list[Reply.Reply]
    ) -> None:
        if isinstance(reply, Reply.Reply):
            message = self._generateNumericReply(client, reply)
        else:
            message = ""
            for each in reply:
                message += self._generateNumericReply(client, each)

        client.handler.send(message)

    def _generateNumericReply(self, client: Client, reply: Reply.Reply) -> str:
        return (
            f"{self.serverState.getPrefix()}"
            f" {reply.code}"
            f" {client.user.nick}"
            f" {reply.text}\r\n"
        )

    def _sendToChannel(
        self,
        sender: Client,
        channel: Channel,
        message: str,
        excludeSender: bool = False,
    ) -> None:
        for username in channel.getAllUsers():
            client = self.serverState.clients[username]
            if excludeSender and client == sender:
                continue

            client.handler.send(f":{sender.getIdentifier()} {message}\r\n")
