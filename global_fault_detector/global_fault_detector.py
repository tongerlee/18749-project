import socket
import sys
import time
from datetime import datetime

# Create a TCP/IP socket
from threading import Thread

numMembers = 0
alive_message = "Server is alive."
dead_message = "Server is dead."


def recvfromlfd(connection, client_address):
    global numMembers
    try:
        print('Connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1024).decode("utf-8")
            print('GFD received "%s" from LFD' % data)
            if numMembers == 0:
                if data == alive_message:
                    numMembers = 1
            if numMembers > 0:
                if data == dead_message:
                    numMembers = 0
            if not data:
            #     print('Sending data back to the client')
            #     connection.sendall(data)
            # else:
                print('No more data from LFD', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()


def recv():
    # Receiving from LFDs at port 8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    # server_address = ('128.237.198.254', 8000)
    server_address = (socket.gethostbyname("Jiatongs-MBP.wv.cc.cmu.edu"), 8000)
    print('GFD starting up on %s port %s' % server_address)
    sock.bind(server_address)
    # Listen for LFD
    sock.listen(3)
    while True:
        print('Waiting for new connection')
        c, addr = sock.accept()  # Establish connection with client.
        Thread(target=recvfromlfd, args=(c, addr)).start()


def send():
    global numMembers
    # Send to RM
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (socket.gethostbyname("Jiatongs-MBP.wv.cc.cmu.edu"), 10000)
    print('Connecting to %s port %s' % server_address)
    sock.connect(server_address)
    # Send data to RM
    while True:
        time.sleep(10)
        now = datetime.now()
        message = str(numMembers)
        # print('%s Sending message to RM "%s"' % (str(datetime.now()), message))
        sock.sendall(str.encode(message))


Thread(target=recv).start()
Thread(target=send).start()


