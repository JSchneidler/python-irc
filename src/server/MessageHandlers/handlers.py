from .Cap import Cap
from .Error import Error
from .Join import Join
from .Kick import Kick
from .List import List
from .LUsers import LUsers
from .Mode import Mode
from .Motd import Motd
from .Names import Names
from .Nick import Nick
from .Oper import Oper
from .Part import Part
from .Pass import Pass
from .Ping import Ping
from .PrivMsg import PrivMsg
from .Time import Time
from .Topic import Topic
from .User import User
from .UserHost import UserHost
from .Users import Users


HANDLERS = {
    "CAP": Cap,
    "ERROR": Error,
    "JOIN": Join,
    "KICK": Kick,
    "LIST": List,
    "LUSERS": LUsers,
    "MODE": Mode,
    "MOTD": Motd,
    "NAMES": Names,
    "NICK": Nick,
    "OPER": Oper,
    "PART": Part,
    "PASS": Pass,
    "PING": Ping,
    "PRIVMSG": PrivMsg,
    "TIME": Time,
    "TOPIC": Topic,
    "USER": User,
    "USERHOST": UserHost,
    "USERS": Users,
}
