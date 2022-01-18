from typing import Optional
from socket import socket, AF_INET, SOCK_STREAM
from select import select

from server.IRCServer import Server


def createClient(server: Server) -> socket:
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((server.host, server.port))

    return client


def readLine(client: socket) -> Optional[str]:
    response = readLines(client, 1)
    if response:
        return response[0]
    return None


def readLines(client: socket, lines: int) -> Optional[list[str]]:
    socketIO = client.makefile("r", newline="\r\n")
    ready = select([socketIO], [], [], 5)
    if ready[0]:
        responses: list[str] = []
        for i in range(lines):
            responses.append(socketIO.readline())
        return responses
    return None


def readWelcome(client: socket) -> Optional[list[str]]:
    return readLines(client, 12)


def readJoin(client: socket) -> Optional[list[str]]:
    return readLines(client, 4)


def registerClient(client: socket, nick: str = "test"):
    client.sendall(f"NICK {nick}\r\n".encode())
    client.sendall(f"USER {nick} 0 * *\r\n".encode())
    return readWelcome(client)
