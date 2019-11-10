import socket
import sys
import time
from datetime import datetime

import json
import tcp_client
# Create a TCP/IP socket
from threading import Thread

iplist=[]
myhostname = "Jiatongs-MBP.wv.cc.cmu.edu"
alive_message = "Server is alive."
dead_message = "Server is dead."


def recvfromlfd(connection, client_address):
    global numMembers
    try:
        print('Connection from', client_address)
        client_ip = client_address[0]

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1024).decode("utf-8")
            send_to_rm_flag = False
            print('GFD received "%s" from LFD' % data)
            if alive_message in data:
                if client_ip not in iplist:
                    iplist.append(client_ip)
                    send_to_rm_flag = True
                    print('Added')
            if dead_message in data:
                if client_ip in iplist:
                    iplist.remove(client_ip)
                    send_to_rm_flag = True
                    print('Removed')
            
            if send_to_rm_flag:
                try:
                    tcp_client.send_to(('localhost', 10000), json.dumps(iplist),0)
                except:
                    pass
            if not data:
                print('No more data from LFD', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()


def recv():
    global myhostname
    # Receiving from LFDs at port 8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    # server_address = ('128.237.198.254', 8000)
    server_address = ('localhost', 8000)
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
    global myhostname
    # Send to RM
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (socket.gethostbyname(myhostname), 10000)
    print('Connecting to %s port %s' % server_address)
    sock.connect(server_address)
    # Send data to RM
    while True:
        time.sleep(5)
        now = datetime.now()
        message = str(numMembers)
        # print('%s Sending message to RM "%s"' % (str(datetime.now()), message))
        sock.sendall(str.encode(message))


Thread(target=recv).start()
#Thread(target=send).start()


