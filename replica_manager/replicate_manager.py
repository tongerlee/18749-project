# function of print (timestamp: n members)
# list of replica: n = len(list)
# receive message from Global Fault detector
import socket
import sys
import time
from datetime import datetime
from threading import Thread
import json
# # Create a TCP/IP socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # Bind the socket to the port
# server_address = (socket.gethostbyname("Jiatongs-MBP.wv.cc.cmu.edu"), 10000)
# # server_address = ('128.237.198.254', 8000)
# print(sys.stderr, 'starting up on %s port %s' % server_address)
# sock.bind(server_address)
# # Listen for incoming connections
# sock.listen(1)

# while True:
#     # Wait for a connection
#     print(sys.stderr, 'waiting for a connection')
#     connection, client_address = sock.accept()
#     # try:
#     print(sys.stderr, 'connection from', client_address)

#     # Receive the data in small chunks and retransmit it
#     while True:
#         data = connection.recv(16)
#         current_timestamp = str(datetime.now())
#         # print(sys.stderr, current_timestamp + ': ' + str(data) + ' members')
#         print("%s: %s members" % (current_timestamp, data.decode("utf-8")))
#         if not data:
#             print ("No receive data from GFD")
#             # sleep(10)
#             break

myhostname = "localhost"
numMembers = 0
membesIP = 0

def recvfrom(connection, client_address):
    global numMembers
    global membersIP
    try:
        print('Connection from', client_address)

        # Receive the data in small chunks and retransmit it

        while True:
            #data = connection.recv(1024).decode("utf-8")
           # print("RM received",data)

            try:
                current_timestamp = str(datetime.now())
                data = json.loads(data = connection.recv(1024))
                for ip in data:
                    ip = tuple(ip,"8080")
                membersIP = data

                print(current_timestamp + "  Num of members: " + numMembers)
            except json.decoder.JSONDecodeError as e:
                #data =  connection.recv(1024).decode("utf-8")
                message = json.dumps(membersIP)
                numMembers = len(membersIP)
                send(client_address, message)
                            
            if not data:
                print('No more data', client_address)
                break


    finally:
        # Clean up the connection
        connection.close()



def recv():
    global myhostname

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (socket.gethostbyname(myhostname), 10000)
    print('RM starting up on %s port %s' % server_address)
    sock.bind(server_address)

    sock.listen(3)
    while True:
        print('Waiting for new connection')
        c, addr = sock.accept()  # Establish connection with client.
        Thread(target=recvfrom, args=(c, addr)).start()

def send(server_address, message):

    #global myhostname

    #server_address = (socket.gethostbyname(myhostname), 10000)
    print('Connecting to %s port %s' % server_address)
    sock.connect(server_address)
    # Send data to RM

    time.sleep(1)
    now = datetime.now()
    #message = str(numMembers)
        # print('%s Sending message to RM "%s"' % (str(datetime.now()), message))
    sock.sendall(str.encode(message))


Thread(target = recv).start()
