from colorama import init, Fore, Back
from enum import Enum
from logging import Formatter, StreamHandler, Logger, getLogger

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


class StandardLogger(Logger):
    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        super().__init__(name)
        self.setLevel(level.value)
        self.addHandler(stdOut)

    def setAllLevels(self, level: LogLevel) -> None:
        self.setLevel(level.value)
        for handler in self.handlers:
            handler.setLevel(level.value)


# logger = StandardLogger("irc")
logger = getLogger("irc")
logger.addHandler(stdOut)
