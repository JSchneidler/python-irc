from irc.logger import logger

from .IRCServer import Server
from .config import Config


def main():
    config = Config()
    logger.setLevel(config.getLogLevel().value)
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
