from pytest import fixture
import threading
import socket

from server.IRCServer import Server

SERVER_HOST = "localhost"
SERVER_PORT = 0


@fixture
def server():
    server = Server(SERVER_HOST, SERVER_PORT, "test")
    serverThread = threading.Thread(target=server.start)
    serverThread.start()

    yield server

    server.stop()
    serverThread.join()


def createClient(server: Server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server.host, server.port))

    return client


def test_IRCServer_connect(server):
    createClient(server)


def test_IRCServer_connectMultipleClients(server):
    createClient(server)
    createClient(server)


def test_IRCServer_pass(server):
    client = createClient(server)
    client.sendall(b"PASS password\r\n")


def test_IRCServer_pass_notEnoughParameters(server):
    client = createClient(server)
    client.sendall(b"PASS\r\n")
    response = client.recv(1024).decode("utf-8")

    assert response == ":127.0.0.1 461 PASS :Not enough parameters"


def test_IRCServer_nick(server):
    client = createClient(server)
    client.sendall(b"NICK nickname\r\n")


def test_IRCServer_nick_noNicknameGiven(server):
    client = createClient(server)
    client.sendall(b"NICK\r\n")
    response = client.recv(1024).decode("utf-8")

    assert response == ":127.0.0.1 431 :No nickname given"


def test_IRCServer_user(server):
    client = createClient(server)
    client.sendall(b"NICK guest\r\n")
    client.sendall(b"USER guest 0 :Full Name\r\n")

    responses = []
    for i in range(7):
        responses.append(client.recv(1024).decode("utf-8"))

    expectedResponses = [
        ":127.0.0.1 001 :Welcome to the Internet Relay Network\r\nguest!guest@127.0.0.1",
        ":127.0.0.1 002 :Your host is 127.0.0.1, running version 0.0.1",
        ":127.0.0.1 003 :This server was created None",
        ":127.0.0.1 004 :127.0.0.1 0.0.1 aiwroOs OovaimnqpsrtklbeI",
        ":127.0.0.1 251 :There are 0 users and 0 services on 1 server",
        ":127.0.0.1 252 0 :operator(s) online",
        ":127.0.0.1 253 1 :unknown connection(s)",
    ]
    assert responses == expectedResponses


def test_IRCServer_user_notEnoughParameters(server):
    client = createClient(server)
    client.sendall(b"USER\r\n")
    response = client.recv(1024).decode("utf-8")

    assert response == ":127.0.0.1 461 USER :Not enough parameters"
