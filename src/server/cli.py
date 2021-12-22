import argparse
import logging
from typing import NamedTuple

from server.IRCServer import Server


class CliArguments(NamedTuple):
    host: str
    port: int
    log_level: str


parser = argparse.ArgumentParser(description="Run an IRC server.")
parser.add_argument("--host", type=str, default="localhost", help="Host to listen on")
parser.add_argument("-p", "--port", type=int, default=6667, help="Port to listen on")
parser.add_argument(
    "-l",
    "--log_level",
    type=str,
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="INFO",
    help="Log level",
)

args: CliArguments = parser.parse_args()

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def main():
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
