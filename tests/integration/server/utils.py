from typing import Callable
from socket import socket, AF_INET, SOCK_STREAM

from server.IRCServer import Server


def createClient(server: Server) -> socket:
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((server.host, server.port))

    return client


def readLine(client: socket):
    return client.recv(1024).decode()


def readFactory(client) -> Callable:
    def read(lines: int) -> list[str]:
        responses = []
        for i in range(lines):
            responses.append(readLine(client))
        return responses

    return read


def readWelcome(client) -> list[str]:
    return readFactory(client)(12)


def readJoin(client) -> list[str]:
    return readFactory(client)(4)


def registerClient(client: socket, nick: str = "test"):
    client.sendall(f"NICK {nick}\r\n".encode())
    client.sendall(f"USER {nick} 0 * *\r\n".encode())
    return readWelcome(client)
