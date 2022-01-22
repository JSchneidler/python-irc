from socket import socket

from server.Server import Server

from .utils import createClient, readLine, registerClient


def test_Server_pass(client: socket):
    client.sendall(b"PASS password\r\n")


def test_Server_pass_notEnoughParameters(client: socket):
    client.sendall(b"PASS\r\n")
    response = readLine(client)

    assert response == ":127.0.0.1 461 * PASS :Not enough parameters\r\n"


def test_Server_nick(client: socket):
    client.sendall(b"NICK nickname\r\n")


def test_Server_nick_noNicknameGiven(client: socket):
    client.sendall(b"NICK\r\n")
    response = readLine(client)

    assert response == ":127.0.0.1 431 * :No nickname given\r\n"


def test_Server_nick_nicknameInUse(server: Server):
    client = createClient(server)
    client.sendall(b"NICK test\r\n")
    client2 = createClient(server)
    client2.sendall(b"NICK test\r\n")
    response = readLine(client2)

    assert response == ":127.0.0.1 433 * test :Nickname is already in use\r\n"


def test_Server_user(client: socket):
    responses = registerClient(client)

    expectedResponses = [
        ":127.0.0.1 001 test :Welcome to the Internet Relay Network test!test@127.0.0.1\r\n",
        ":127.0.0.1 002 test :Your host is 127.0.0.1, running version 0.0.1\r\n",
        ":127.0.0.1 003 test :This server was created N/A\r\n",
        ":127.0.0.1 004 test :127.0.0.1 0.0.1 aiwroOs OovaimnqpsrtklbeI\r\n",
        ":127.0.0.1 251 test :There are 1 users and 0 services on 1 server\r\n",
        ":127.0.0.1 252 test 0 :operator(s) online\r\n",
        ":127.0.0.1 253 test 0 :unknown connection(s)\r\n",
        ":127.0.0.1 254 test 0 :channels formed\r\n",
        ":127.0.0.1 255 test :I have 1 clients and 0 servers\r\n",
        ":127.0.0.1 375 test :- 127.0.0.1 Message of the day - \r\n",
        ":127.0.0.1 372 test :- test\r\n",
        ":127.0.0.1 376 test :End of MOTD command\r\n",
    ]

    assert responses == expectedResponses


def test_Server_user_notEnoughParameters(client: socket):
    client.sendall(b"USER\r\n")
    response = readLine(client)

    assert response == ":127.0.0.1 461 * USER :Not enough parameters\r\n"
