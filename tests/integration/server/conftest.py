from pytest import fixture
from typing import Generator
from threading import Thread
from socket import socket
from bcrypt import hashpw, gensalt

from server.Server import Server
from server.ServerState import OperatorCredential

from .utils import createClient

SERVER_HOST = "localhost"
SERVER_PORT = 0

operatorCredentials = [
    OperatorCredential(
        hashpw("test".encode(), gensalt()), hashpw("test".encode(), gensalt())
    )
]


@fixture
def server() -> Generator[Server, None, None]:
    server = Server(SERVER_HOST, SERVER_PORT, ["test"], operatorCredentials, "N/A")
    serverThread = Thread(target=server.start, daemon=True)
    serverThread.start()

    yield server

    server.stop()
    serverThread.join()


@fixture
def client(server: Server) -> Generator[socket, None, None]:
    client = createClient(server)
    yield client
    client.close()
