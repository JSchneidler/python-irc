from socket import socket

from .utils import readLine


def test_Server_oper(client: socket):
    client.sendall(b"OPER test test\r\n")
    response = readLine(client)

    assert response == ":127.0.0.1 381 * :You are now an IRC operator\r\n"


def test_Server_oper_notEnoughParameters(client: socket):
    client.sendall(b"OPER\r\n")
    response = readLine(client)

    assert response == ":127.0.0.1 461 * OPER :Not enough parameters\r\n"

    client.sendall(b"OPER test\r\n")
    response = readLine(client)

    assert response == ":127.0.0.1 461 * OPER :Not enough parameters\r\n"


def test_Server_oper_passwordMismatch(client: socket):
    client.sendall(b"OPER pass pass\r\n")
    response = readLine(client)

    assert response == ":127.0.0.1 464 * :Password incorrect\r\n"
