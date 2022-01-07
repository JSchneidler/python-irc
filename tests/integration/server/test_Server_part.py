from socket import socket

from .utils import readLine, registerClient, readJoin


def test_Server_part(client: socket):
    registerClient(client)
    client.sendall(b"JOIN #chan\r\n")
    readJoin(client)
    client.sendall(b"PART #chan Tired\r\n")
    response = readLine(client)

    assert response == ":test!test@127.0.0.1 PART #chan :Tired\r\n"
