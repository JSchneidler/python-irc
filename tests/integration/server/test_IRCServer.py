from pytest import fixture
import threading
import socket

from server.IRCServer import Server

SERVER_HOST = "localhost"
SERVER_PORT = 0


@fixture
def server():
    server = Server(SERVER_HOST, SERVER_PORT, ["test"], "N/A")
    serverThread = threading.Thread(target=server.start)
    serverThread.start()

    yield server

    server.stop()
    serverThread.join()


def createClient(server: Server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server.host, server.port))

    return client


def readFactory(client):
    def read(lines: int):
        responses = []
        for i in range(lines):
            responses.append(client.recv(1024).decode("utf-8"))
        return responses

    return read


def readWelcome(client):
    return readFactory(client)(12)


def readJoin(client):
    return readFactory(client)(4)


def test_Server_connect(server):
    createClient(server)


def test_Server_connectMultipleClients(server):
    createClient(server)
    createClient(server)


def test_Server_cap(server):
    client = createClient(server)
    expectedResponse = "CAP * LS :\r\n"

    client.sendall(b"CAP LS\r\n")
    response = client.recv(1024).decode("utf-8")
    assert response == expectedResponse

    client.sendall(b"CAP LS 302\r\n")
    response = client.recv(1024).decode("utf-8")
    assert response == expectedResponse


def test_Server_pass(server):
    client = createClient(server)
    client.sendall(b"PASS password\r\n")


def test_Server_pass_notEnoughParameters(server):
    client = createClient(server)
    client.sendall(b"PASS\r\n")
    response = client.recv(1024).decode("utf-8")

    assert response == ":127.0.0.1 None 461 PASS :Not enough parameters\r\n"


def test_Server_nick(server):
    client = createClient(server)
    client.sendall(b"NICK nickname\r\n")


def test_Server_nick_noNicknameGiven(server):
    client = createClient(server)
    client.sendall(b"NICK\r\n")
    response = client.recv(1024).decode("utf-8")

    assert response == ":127.0.0.1 None 431 :No nickname given\r\n"


def test_Server_user(server):
    client = createClient(server)
    client.sendall(b"NICK guest\r\n")
    client.sendall(b"USER guest 0 * *\r\n")

    responses = readWelcome(client)

    expectedResponses = [
        ":127.0.0.1 guest 001 :Welcome to the Internet Relay Network\r\nguest!guest@127.0.0.1\r\n",
        ":127.0.0.1 guest 002 :Your host is 127.0.0.1, running version 0.0.1\r\n",
        ":127.0.0.1 guest 003 :This server was created N/A\r\n",
        ":127.0.0.1 guest 004 :127.0.0.1 0.0.1 aiwroOs OovaimnqpsrtklbeI\r\n",
        ":127.0.0.1 guest 251 :There are 0 users and 0 services on 1 server\r\n",
        ":127.0.0.1 guest 252 0 :operator(s) online\r\n",
        ":127.0.0.1 guest 253 1 :unknown connection(s)\r\n",
        ":127.0.0.1 guest 254 0 :channels formed\r\n",
        ":127.0.0.1 guest 255 :I have 0 clients and 0 servers\r\n",
        ":127.0.0.1 guest 375 :- 127.0.0.1 Message of the day - \r\n",
        ":127.0.0.1 guest 372 :- test\r\n",
        ":127.0.0.1 guest 376 :End of MOTD command\r\n",
    ]
    assert responses == expectedResponses


def test_Server_user_notEnoughParameters(server):
    client = createClient(server)
    client.sendall(b"USER\r\n")
    response = client.recv(1024).decode("utf-8")

    assert response == ":127.0.0.1 None 461 USER :Not enough parameters\r\n"


def test_Server_join(server):
    client = createClient(server)
    client.sendall(b"NICK guest\r\n")
    client.sendall(b"USER guest 0 * *\r\n")
    readWelcome(client)
    client.sendall(b"JOIN #test\r\n")

    responses = readJoin(client)

    expectedResponses = [
        ":guest!guest@127.0.0.1 JOIN #test\r\n",
        "#test :No topic is set\r\n",
        ":127.0.0.1 guest 353 #test = guest :guest\r\n",
        ":127.0.0.1 guest 366 guest #test :End of NAMES list\r\n",
    ]

    assert responses == expectedResponses


def test_Server_join_notEnoughParameters(server):
    client = createClient(server)
    client.sendall(b"NICK guest\r\n")
    client.sendall(b"USER guest 0 * *\r\n")
    readWelcome(client)
    client.sendall(b"JOIN\r\n")
    response = client.recv(1024).decode("utf-8")

    assert response == ":127.0.0.1 guest 461 JOIN :Not enough parameters\r\n"


def test_Server_part(server):
    client = createClient(server)
    client.sendall(b"NICK guest\r\n")
    client.sendall(b"USER guest 0 * *\r\n")
    readWelcome(client)
    client.sendall(b"JOIN #test\r\n")
    readJoin(client)
    client.sendall(b"PART #test Tired\r\n")
    response = client.recv(1024).decode("utf-8")

    assert response == ":guest!guest@127.0.0.1 PART #test :Tired\r\n"
