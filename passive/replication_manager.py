import socket
import sys
import time
from datetime import datetime
from threading import Thread
import json

# myhostname = "chenweideMacBook-Pro.local"
myhostname = socket.gethostname()
numMembers = 0
membersIP = []


def recvfromClient(connection, client_address, sock):
    global numMembers
    global membersIP
    numServer = 0

    try:
        print('Connection from client', client_address)

        # Receive the data in small chunks and retransmit it
        connection.sendall(str.encode(json.dumps(membersIP)))
        while True:
            try:
                current_timestamp = str(datetime.now())
                # sending new ip tuple list to all servers
                if len(membersIP) != numServer:
                    print("Broadcasting new list of ips to all clients")
                    connection.sendall(str.encode(json.dumps(membersIP)))
                    numServer = len(membersIP)
            except json.decoder.JSONDecodeError as e:
                message = json.dumps(membersIP)
                numMembers = len(membersIP)
                try:
                    print("error here ", e)
                except:
                    pass
                # data = message
            # if not data:
                # print('No more data', client_address)
                # break
    finally:
        # Clean up the connection
        connection.close()

def recvfrom(connection, client_address):
    global numMembers
    global membersIP
    try:
        print('Connection from', client_address)

        # Receive the data in small chunks and retransmit it

        while True:
            data = connection.recv(1024)
            # print("RM received",data)
            if data != None:
                try:
                    current_timestamp = str(datetime.now())
                    # data = connection.recv(1024)
                    data = json.loads(data)
                    ip_list = data['ip_list']
                    ip_tuple = []
                    for ip in ip_list:
                        ip = (ip, 8084)
                        ip_tuple.append(ip)
                    if len(membersIP) != len(ip_tuple):
                        print("Membership changed")
                        print("Broadcasting membership change to all servers")
                        # sending new ip tuple list to all servers
                        new_server = list(set(ip_tuple) - set(membersIP))
                        for server_address in ip_tuple:
                            Thread(target=send, args=(server_address, ip_tuple)).start()

                    membersIP = ip_tuple
                    numMembers = len(membersIP)

                    print(current_timestamp,
                          "\n  Num of members: ", numMembers,
                          "\n ip: ", ip_tuple)
                except json.decoder.JSONDecodeError as e:
                    # data =  connection.recv(1024).decode("utf-8")
                    message = json.dumps(membersIP)
                    numMembers = len(membersIP)
                    try:
                        send(client_address, message)
                    except:
                        pass
                # data = message
            if not data:
                print('No more data', client_address)
                break


    finally:
        # Clean up the connection
        connection.close()


def recv():
    global myhostname

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # server_address = ('localhost', 10000)
    server_address = (socket.gethostbyname(myhostname), 10000)
    print('RM starting up on %s port %s' % server_address)
    sock.bind(server_address)

    sock.listen(3)
    while True:
        print('Waiting for new connection')
        c, addr = sock.accept()  # Establish connection with client.
        Thread(target=recvfrom, args=(c, addr)).start()

def recvClient():
    global myhostname

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # server_address = ('localhost', 10000)
    server_address = (socket.gethostbyname(myhostname), 10001)
    print('RM starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.listen(3)
    while True:
        print('Waiting for new connection')
        c, addr = sock.accept()  # Establish connection with client.
        Thread(target=recvfromClient, args=(c, addr, sock)).start()


def send(server_address, ip_list):
    # global myhostname
    global membersIP
    # server_address = (socket.gethostbyname(myhostname), 10000)
    print('Connecting to %s port %s' % server_address)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    # Send data to RM
    time.sleep(3)
    # now = datetime.now()
    # print('%s Sending message to RM "%s"' % (str(datetime.now()), message))
    message = json.dumps({'ip_list': ip_list, 'num_member': len(membersIP)})
    sock.sendall(str.encode(message))
    sock.close()


Thread(target=recv).start()
Thread(target=recvClient).start()
