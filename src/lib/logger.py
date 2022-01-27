from colorama import init, Fore, Back
from enum import Enum
from logging import FileHandler, Formatter, StreamHandler, getLogger

init(autoreset=True)


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


FILE_FORMATTER = Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

LOG_FORMATTER = Formatter(
    f"{Fore.CYAN}%(asctime)s "
    f"{Fore.BLACK + Back.WHITE}%(levelname)s{Back.BLACK} "
    f"{Fore.GREEN}%(name)s "
    f"{Fore.YELLOW} %(message)s"
)

stdOut = StreamHandler()
# TODO: Use colored formatter only for CLI output
# stdOut.setFormatter(LOG_FORMATTER)

logger = getLogger("irc")
logger.addHandler(stdOut)


def setLogFile(path: str) -> None:
    fileHandler = FileHandler(path)
    fileHandler.setFormatter(FILE_FORMATTER)
    logger.addHandler(fileHandler)
