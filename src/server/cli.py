from lib.logger import logger, setLogFile

from .Server import Server
from .Config import Config


def main():
    config = Config()

    logger.setLevel(config.getLogLevel().value)
    logPath = config.getLogPath()
    if logPath:
        setLogFile(logPath)

    server = Server(
        config.getHost(),
        config.getPort(),
        config.getMOTD(),
        operatorCredentials=config.getOperatorCredentials(),
    )

    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == "__main__":
    main()
