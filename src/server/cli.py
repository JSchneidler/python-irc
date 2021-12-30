from tap import Tap

from irc.logger import LogLevel, logger
from server.IRCServer import Server


class CliArgumentParser(Tap):
    """Run an IRC server."""

    host: str = "localhost"  # Host to listen on
    port: int = 6667  # Port to listen on
    log_level: LogLevel = LogLevel.INFO  # Log level


def main():
    args = CliArgumentParser().parse_args()
    # logger.setAllLevels(args.log_level)
    logger.setLevel(args.log_level.value)
    server = Server(args.host, args.port, ["Welcome to the IRC server!"])

    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == "__main__":
    main()
