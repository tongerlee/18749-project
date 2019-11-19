
import socket
import sys
import time
from datetime import datetime
from threading import Thread
import json


myhostname = "localhost"
numMembers = 0
membersIP = []

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
                    #data = connection.recv(1024)
              
                    data = json.loads(data)
                    data_tuple = []
                    for ip in data_tuple:
                        print(ip)
                        ip = (ip,8080)
                        data_tuple.append(ip)
                    membersIP = data_tuple
                    numMembers = len(membersIP)

                    print(current_timestamp , "  Num of members: " ,numMembers)
                except json.decoder.JSONDecodeError as e:
                    #data =  connection.recv(1024).decode("utf-8")
                    message = json.dumps(membersIP)
                    numMembers = len(membersIP)
                    try:
                        send(client_address, message)
                    except:
                        pass
                #data = message
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
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    # Send data to RM

    time.sleep(1)
    now = datetime.now()
    #message = str(numMembers)
        # print('%s Sending message to RM "%s"' % (str(datetime.now()), message))
    sock.sendall(str.encode(message))


Thread(target = recv).start()
