from socket import socket

from .utils import readLine


def test_Server_mode(client: socket):
    pass


def test_Server_mode_notEnoughParameters(client: socket):
    client.sendall(b"MODE\r\n")
    response = readLine(client)

    assert response == ":127.0.0.1 461 * MODE :Not enough parameters\r\n"
