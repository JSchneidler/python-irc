from socket import socket

from server.IRCServer import Server

from .utils import createClient, readLine


def test_Server_connect(server: Server):
    createClient(server)


def test_Server_connectMultipleClients(server: Server):
    createClient(server)
    createClient(server)


def test_Server_cap(client: socket):
    expectedResponse = "CAP * LS :\r\n"

    client.sendall(b"CAP LS\r\n")
    response = readLine(client)
    assert response == expectedResponse

    client.sendall(b"CAP LS 302\r\n")
    response = readLine(client)
    assert response == expectedResponse


def test_Server_ping(client: socket):
    client.sendall(b"PING\r\n")
    response = readLine(client)

    assert response == "PONG\r\n"
