from tap import Tap
from typing import Literal
import logging

from server.IRCServer import Server


LOG_LEVELS = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class CliArgumentParser(Tap):
    """Run an IRC server."""

    host: str = "localhost"  # Host to listen on
    port: int = 6667  # Port to listen on
    log_level: LOG_LEVELS = "INFO"  # Log level


LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def main():
    args = CliArgumentParser().parse_args()
    logging.basicConfig(level=args.log_level, format=LOG_FORMAT, force=True)
    server = Server(args.host, args.port, ["Welcome to the IRC server!"])

    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == "__main__":
    main()
