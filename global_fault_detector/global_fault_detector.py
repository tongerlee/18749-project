import socket
import sys
import time
from datetime import datetime

# Create a TCP/IP socket
from threading import Thread


def recvfromlfd(connection, client_address):
    try:
        print(sys.stderr, 'connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            print(sys.stderr, 'received "%s"' % data)
            if data:
                print(sys.stderr, 'sending data back to the client')
                connection.sendall(data)
            else:
                print(sys.stderr, 'no more data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()


def recv():
    # Receiving from LFDs at port 8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = ('localhost', 8000)
    print(sys.stderr, 'starting up on %s port %s' % server_address)
    sock.bind(server_address)
    # Listen for LFD
    sock.listen(3)
    while True:
        print(sys.stderr, 'waiting for a connection')
        c, addr = sock.accept()  # Establish connection with client.
        Thread(target=recvfromlfd, args=(c, addr)).start()


def send():
    # Send to RM
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
    print(sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)
    # Send data to RM
    while True:
        time.sleep(10)
        now = datetime.now()
        message = str(now) + "I am GFD. Sending to RM"
        print(sys.stderr, 'sending "%s"' % message)
        sock.sendall(str.encode(message))


Thread(target=recv).start()
Thread(target=send).start()


