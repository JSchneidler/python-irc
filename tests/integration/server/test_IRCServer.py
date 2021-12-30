from socket import socket

from server.IRCServer import Server

from .utils import createClient, readLine, registerClient, readJoin


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
    response = readLine(client)

    assert response == ":127.0.0.1 433 * test :Nickname is already in use\r\n"


def test_Server_user(client: socket):
    responses = registerClient(client)

    expectedResponses = [
        ":127.0.0.1 001 test :Welcome to the Internet Relay Network\r\ntest!test@127.0.0.1\r\n",
        ":127.0.0.1 002 test :Your host is 127.0.0.1, running version 0.0.1\r\n",
        ":127.0.0.1 003 test :This server was created N/A\r\n",
        ":127.0.0.1 004 test :127.0.0.1 0.0.1 aiwroOs OovaimnqpsrtklbeI\r\n",
        ":127.0.0.1 251 test :There are 0 users and 0 services on 1 server\r\n",
        ":127.0.0.1 252 test 0 :operator(s) online\r\n",
        ":127.0.0.1 253 test 1 :unknown connection(s)\r\n",
        ":127.0.0.1 254 test 0 :channels formed\r\n",
        ":127.0.0.1 255 test :I have 0 clients and 0 servers\r\n",
        ":127.0.0.1 375 test :- 127.0.0.1 Message of the day - \r\n",
        ":127.0.0.1 372 test :- test\r\n",
        ":127.0.0.1 376 test :End of MOTD command\r\n",
    ]

    assert responses == expectedResponses


def test_Server_user_notEnoughParameters(client: socket):
    client.sendall(b"USER\r\n")
    response = readLine(client)

    assert response == ":127.0.0.1 461 * USER :Not enough parameters\r\n"


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


def test_Server_part(client: socket):
    registerClient(client)
    client.sendall(b"JOIN #chan\r\n")
    readJoin(client)
    client.sendall(b"PART #chan Tired\r\n")
    response = readLine(client)

    assert response == ":test!test@127.0.0.1 PART #chan :Tired\r\n"


def test_Server_ping(client: socket):
    client.sendall(b"PING\r\n")
    response = readLine(client)

    assert response == "PONG\r\n"
