from pytest import fixture
from typing import Generator
from threading import Thread
from socket import socket

from server.IRCServer import Server

from .utils import createClient

SERVER_HOST = "localhost"
SERVER_PORT = 0


@fixture
def server() -> Generator[Server, None, None]:
    server = Server(SERVER_HOST, SERVER_PORT, ["test"], "N/A")
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
