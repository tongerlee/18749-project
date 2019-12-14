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
    print("********** client start working  *********** ")
    iteration = 0
    while True:

        time.sleep(2)

        # format of message to server : (client_id, inputData)
        inputData = client_id + "," + str(iteration) + ",1"
        iteration += 1
        print("----- sending message: ", str(iteration), " -------")

        # wait until there is at least one server
        while len(server_list) < 1:
            continue
        # print("current server list :", server_list)

        response = "-1"
        back_up_ips = server_list[1:]

        # for primary
        while response == "-1":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            primary_ip = server_list[0][0]
            back_up_ips = server_list[1:]
            try:
                primary_server_address = (primary_ip, server_port)
                #print('connecting to [primary] %s' % primary_ip)
                sock.connect(primary_server_address)
                sock.sendall(str.encode(inputData))
                receiveData = sock.recv(1024).decode("utf-8")

                if receiveData == "":
                    #print('primary %s failed :(' % primary_ip)
                    while len(server_list) < 1 or server_list[0][0] == primary_ip:
                        continue
                    continue

                response = receiveData

                # print received server response
               # print("received: '", response, "' from", primary_ip)
                print('[response] : %s ' % response)

            except:
                #print('primary %s failed :(' % primary_ip)
                while len(server_list) < 1 or server_list[0][0] == primary_ip:
                    continue

            finally:
                sock.close()

        # for backups
        for backup_ip in back_up_ips:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                backup_server_address = (backup_ip[0], server_port)
               # print('connecting to [backup] %s' % backup_ip[0])
                sock.connect(backup_server_address)
                sock.sendall(str.encode(inputData))

            except:
                #print('backup %s failed :(' % backup_ip[0])
                pass
            finally:
                sock.close()


def connect_replicate_manager():
    global server_list
    global rm_IP
    global rm_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (rm_IP, rm_port)
    while len(server_list) < 1:
        try:
           # print('connecting to rm %s ...' % rm_IP)
            sock.connect(server_address)
            # on connection, receive membership from rm
            data = sock.recv(1024)
            data = json.loads(data)
            server_list = data
            # print membership
            print("############ receiving membership from rm #############")
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
                print("############ receiving membership from rm #############")
                for ip in server_list:
                    print('%s' % ip[0])
        except:
        # except json.decoder.JSONDecodeError as e:
            # print(e)
            pass
        finally:
            print('*********** closing socket **************')
            sock.close()


Thread(target=connect_replicate_manager()).start()