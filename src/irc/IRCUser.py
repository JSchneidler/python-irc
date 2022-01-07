from dataclasses import dataclass
from typing import Optional

MAX_NICK_LENGTH = 9


@dataclass
class Modes:
    away: bool = False
    invisible: bool = False
    operator: bool = False


class User:
    password: Optional[str] = None
    nick: str = "*"
    username: Optional[str] = None
    realname: Optional[str] = None
    modes: Modes = Modes()

    def setNick(self, nick: str) -> None:
        if len(nick) > MAX_NICK_LENGTH:
            raise ValueError("Nick is too long")
        self.nick = nick

    def getModes(self) -> str:
        modes = ""
        if self.isAway():
            modes += "a"
        if self.isInvisible():
            modes += "i"
        if self.isOperator():
            modes += "o"
        return modes

    def isAway(self) -> bool:
        return self.modes.away

    def setAway(self, away: bool) -> None:
        self.modes.away = away

    def isInvisible(self) -> bool:
        return self.modes.invisible

    def setInvisible(self, invisible: bool) -> None:
        self.modes.invisible = invisible

    def isOperator(self) -> bool:
        return self.modes.operator

    def setOperator(self, operator: bool) -> None:
        self.modes.operator = operator


Users = dict[str, User]
