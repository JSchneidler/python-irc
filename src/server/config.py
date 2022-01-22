from typing import Optional

from tap import Tap
from pydantic import BaseSettings

from lib.logger import LogLevel

from .ServerState import OperatorCredential, OperatorCredentials, MOTD


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 6667
DEFAULT_LOG_LEVEL = LogLevel.INFO


class CliConfig(Tap):
    """Run an IRC server."""

    host: Optional[str] = None  # Host to listen on
    port: Optional[int] = None  # Port to listen on
    log_level: Optional[LogLevel] = None  # Log level


class FileConfig(BaseSettings):
    host: Optional[str] = None  # Host to listen on
    port: Optional[int] = None  # Port to listen on
    log_level: Optional[LogLevel] = None  # Log level
    operator_credentials_path: Optional[str] = None  # Path to operator credentials file
    motd_path: Optional[str] = None  # Path to MOTD file

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Config:
    cliConfig: CliConfig
    fileConfig: FileConfig

    operatorCredentials: Optional[OperatorCredentials]
    motd: Optional[MOTD]

    def __init__(self):
        self.cliConfig = CliConfig().parse_args()
        self.fileConfig = FileConfig()

        self.loadOperatorCredentials()
        self.loadMOTD()

    def loadOperatorCredentials(self) -> None:
        if self.fileConfig.operator_credentials_path:
            with open(self.fileConfig.operator_credentials_path, "r") as f:
                operatorCredentials: OperatorCredentials = []
                for line in f.readlines():
                    [userHash, passwordHash] = line.strip().split(":")
                    operatorCredentials.append(
                        OperatorCredential(userHash.encode(), passwordHash.encode())
                    )
                if len(operatorCredentials) > 0:
                    self.operatorCredentials = operatorCredentials
                else:
                    self.operatorCredentials = None
        else:
            self.operatorCredentials = None

    def loadMOTD(self) -> None:
        if self.fileConfig.motd_path:
            with open(self.fileConfig.motd_path, "r") as f:
                self.motd = [line.strip() for line in f.readlines()]
        else:
            self.motd = None

    def getHost(self) -> str:
        return self.cliConfig.host or self.fileConfig.host or DEFAULT_HOST

    def getPort(self) -> int:
        return self.cliConfig.port or self.fileConfig.port or DEFAULT_PORT

    def getLogLevel(self) -> LogLevel:
        return (
            self.cliConfig.log_level or self.fileConfig.log_level or DEFAULT_LOG_LEVEL
        )

    def getOperatorCredentials(self) -> Optional[OperatorCredentials]:
        return self.operatorCredentials

    def getMOTD(self) -> Optional[MOTD]:
        return self.motd
