from typing import Callable, Optional, TextIO
from socket import socket, AF_INET, SOCK_STREAM
from select import select

from server.IRCServer import Server


def createClient(server: Server) -> socket:
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((server.host, server.port))

    return client


def readLine(client: socket) -> Optional[str]:
    socketIO = client.makefile("r", newline="\r\n")
    ready = select([socketIO], [], [], 2)
    if ready[0]:
        return socketIO.readline()
    return None


def readFactory(client: socket) -> Callable:
    def read(lines: int) -> list[Optional[str]]:
        responses = []
        for i in range(lines):
            responses.append(readLine(client))
        return responses

    return read


def readWelcome(client: socket) -> list[str]:
    return readFactory(client)(12)


def readJoin(client: socket) -> list[str]:
    return readFactory(client)(4)


def registerClient(client: socket, nick: str = "test"):
    client.sendall(f"NICK {nick}\r\n".encode())
    client.sendall(f"USER {nick} 0 * *\r\n".encode())
    return readWelcome(client)
