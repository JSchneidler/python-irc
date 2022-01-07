from socket import socket

from server.IRCServer import Server

from .utils import createClient, readLine, registerClient, readJoin


def test_Server_join(client: socket):
    registerClient(client)
    client.sendall(b"JOIN #chan\r\n")

    responses = readJoin(client)

    expectedResponses = [
        ":test!test@127.0.0.1 JOIN #chan\r\n",
        ":127.0.0.1 331 test #chan :No topic is set\r\n",
        ":127.0.0.1 353 test = #chan :@test\r\n",
        ":127.0.0.1 366 test #chan :End of NAMES list\r\n",
    ]

    assert responses == expectedResponses


def test_Server_join_notEnoughParameters(client: socket):
    registerClient(client)
    client.sendall(b"JOIN\r\n")
    response = readLine(client)

    assert response == ":127.0.0.1 461 test JOIN :Not enough parameters\r\n"


def test_Server_join_channelKey(server: Server):
    client = createClient(server)
    client2 = createClient(server)
    registerClient(client, "test")
    registerClient(client2, "test2")

    client.sendall(b"JOIN #chan password\r\n")
    readJoin(client)

    client2.sendall(b"JOIN #chan pass\r\n")
    response = readLine(client2)
    assert (
        response == ":127.0.0.1 475 test2 #chan :Cannot join channel (+k)\r\n"
    )

    client2.sendall(b"JOIN #chan password\r\n")
    responses = readJoin(client2)
    expectedResponses = [
        ":test2!test2@127.0.0.1 JOIN #chan\r\n",
        ":127.0.0.1 331 test2 #chan :No topic is set\r\n",
        ":127.0.0.1 353 test2 = #chan :@test test2\r\n",
        ":127.0.0.1 366 test2 #chan :End of NAMES list\r\n",
    ]
    assert responses == expectedResponses
