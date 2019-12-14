import json
import socket
import sys
import time
from threading import Thread

client_id = sys.argv[1]
rm_IP = socket.gethostbyname(socket.gethostname())
rm_port = 10001
server_port = 8080
server_list = []


def work():
    global server_list
    global server_port
    global client_id
    print("********** Now client can start requesting *********** ")
    iteration = 0
    while True:

        time.sleep(2)

        # format of message to server : (client_id, inputData)
        inputData = client_id + "," + str(iteration) + ",1"
        iteration += 1
        print("message sending to server :", inputData)

        # request server one by one
        response = ""

        # wait until there is at least one server
        while True:
            if len(server_list) > 0:
                cur_server_list = server_list
                break

        for ip in cur_server_list:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server_address = (ip[0], server_port)
                # print('connecting to server %s port %s' % server_address)
                sock.connect(server_address)

                sock.sendall(str.encode(inputData))

                receiveData = sock.recv(1024).decode("utf-8")

                # print received server response
                print(ip[0], ",", time.ctime(), ",", receiveData)

                # if there is a response, update response
                if receiveData != "not ready":
                    response = receiveData
            except:
                pass
            finally:
                sock.close()

        # print response one time
        if response != "":
            print('[response] : %s' % response)
        else:
            print('failed to get an response !')


def connect_replicate_manager():
    global server_list
    global rm_IP
    global rm_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (rm_IP, rm_port)
    print('connecting to rm at %s port %s ...' % server_address)
    sock.connect(server_address)
    try:

        # on connection, receive membership from rm
        data = sock.recv(1024)
        data = json.loads(data)
        server_list = data
        # print membership
        print("--------- receiving membership from rm -------")
        for ip in server_list:
            print('%s' % ip[0])

        # now can send request to servers
        Thread(target=work).start()

        # if membership changed, receive new membership from rm
        while True:
            data = sock.recv(1024)
            data = json.loads(data)
            server_list = data
            # print new membership
            print("--------- receiving membership from rm -------")
            for ip in server_list:
                print('%s' % ip[0])

    finally:
        print('*********** closing socket **************')
        sock.close()


Thread(target=connect_replicate_manager()).start()