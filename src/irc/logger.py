from colorama import init, Fore, Back
from enum import Enum
from logging import Formatter, StreamHandler, getLogger

init(autoreset=True)


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


LOG_FORMATTER = Formatter(
    f"{Fore.CYAN}%(asctime)s "
    f"{Fore.BLACK + Back.WHITE}%(levelname)s{Back.BLACK} "
    f"{Fore.GREEN}%(name)s "
    f"{Fore.YELLOW} %(message)s"
)
stdOut = StreamHandler()
stdOut.setFormatter(LOG_FORMATTER)

logger = getLogger("irc")
logger.addHandler(stdOut)
