import json
import socket
import sys
from threading import Thread

server_list = []


def read_input():
    global server_list
    print("Now you can input things ... ")
    while True:
        inputData = sys.stdin.readline()
        response = ""
        for ip in server_list:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server_address = (ip, 8080)
                print(sys.stderr, 'connecting to server %s port %s' % server_address)
                sock.connect(server_address)
                sock.sendall(str.encode(inputData))
                receiveData = sock.recv(1024)
                response = receiveData
            except:
                pass
            finally:
                sock.close()
        if response != "":
            print('%s' % response)


def connect_replicate_manager():
    global server_list
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the RM is listening
    server_address = ('localhost', 10000)
    print(sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)
    try:
        message = sys.stdin.readline()
        print(sys.stderr, 'sending "%s" ' % message)
        sock.sendall(str.encode(message))
        data = sock.recv(1024)
        data = json.loads(data)
        server_list = data
        for ip in server_list:
            print(sys.stderr, 'received ip: "%s"' % ip)
        Thread(target=read_input).start()
        while True:
            data = sock.recv(1024)
            data = json.loads(data)
            server_list = data
            for ip in server_list:
                print(sys.stderr, 'received ip: "%s"' % ip)
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()


Thread(target=connect_replicate_manager()).start()
