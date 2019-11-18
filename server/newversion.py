import socket
import threading
import time
import json
import sys
from datetime import datetime
from queue import Queue

# number of messages processed for c1, c2 and queue of messages from c1,c2
mc1, mc2, q = None, None, None

clientMap = None

class Server():
    def __init__(self):
        # initialize variable
        # # listen for checkpoint request
        #global mc, q
        #mc = 0, 0
        self.clientMap = {"1": None, "2": None}
        self.q = Queue()
        self.lockReady = threading.Lock()
        self.isReady = True

    def handle_client(self, host, port):
        print("start client thread")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((socket.gethostbyname(host), port))

        sock.listen(5)
        print("listening to : ", host, port)

        while True:
            client, address = sock.accept()
            try:
                print('connecting from client: ', address)
                while True:
                    data = client.recv(1024)
                    if data:
                        self.lockReady.acquire()
                        if self.isReady:
                            self.lockReady.release()
                            parts = data.split(",")
                            clientId = parts[0]
                            data = parts[1]
                            clientMap[clientId] = data
                            print(time.ctime(), data)
                        else:
                            self.lockReady.release()
                            q.put(data)
                    else:
                        # print('no more data from', address)
                        break
            finally:
                client.close()

    def handle_lfd(self, host, port):
        print("start local fault detector thread")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((socket.gethostbyname(host), port))

        sock.listen(5)
        print("listening to : ", host, port)

        while True:
            client, address = sock.accept()
            try:
                print('connecting from lfd: ', address)
                while True:
                    data = client.recv(1024)
                    if data:
                        if data.decode("utf-8") == 'alive':
                            client.sendall(data)
                    else:
                        # print('no more data from', address)
                        break
            finally:
                client.close()

    def handle_rm(self, host, port):
        print("start replication manager thread")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((socket.gethostbyname(host), port))

        sock.listen(5)
        print("listening to : ", host, port)

        while True:
            client, address = sock.accept()
            try:
                print('connecting from rm: ', address)
                while True:
                    data = client.recv(1024)
                    if data:
                        self.lockReady.acquire()
                        isReady = False
                        self.lockReady.release()
                        #parse received data
                        parts = data.split(",")
                        new_ip = parts[0]
                        port = parts[1]
                        # prepare checkpoint
                        checkpoint = prepareCheckpoint()
                        send_to_new_replica(checkpoint, new_ip, port)

                        while not q.empty():
                            msg = q.get()
                            parts = msg.split(",")
                            clientId = parts[0]
                            msg = parts[1]
                            clientMap[clientId] = msg
                            print(time.ctime(), msg)

                        self.lockReady.acquire()
                        isReady = True
                        self.lockReady.release()
                    else:
                        # print('no more data from', address)
                        break
            finally:
                client.close()

    def handle_rec_checkpoint(self, host, port):
        # send ip, port to RM
        """
        :param checkpoint: JSON
        :return:
        """
        print("start rec_checkpoint thread")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((socket.gethostbyname(host), port))
        sock.listen(1)
        print("listening to : ", host, port)
        #print(sys.stderr, 'starting up on %s port %s' % server_address)

        while True:
            # Wait for a connection
            connection, client_address = sock.accept()

            # Receive the data in small chunks and retransmit it
            while True:
                raw_data = connection.recv(4096)  #???
                current_timestamp = str(datetime.now())
                print(raw_data)
                data = json.loads(raw_data)
                if not data:
                    print ("No receive data from Server")
                    break
                print(parse_data(data))

    def send_to_new_replica(state, new_ip, port):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the new replica is listening
        print('Connecting to new replica at %s port %s' % server_address)
        sock.connect((new_ip, port))
        time.sleep(5)
        sock.sendall(str.encode(state))
        print('State sent to new replica at %s port %s' % server_address)
        sock.close()

    def prepareCheckpoint():
        global mc1, mc2, q1, q2
        mc1 = 3
        mc2 = 4
        q1.put(1)
        q1.put(1)
        q2.put(1)
        encode_variable = json.dumps({mc1 : list(q1.queue), mc2: list(q2.queue)})
        print(str.encode(encode_variable))
        print(type(json.loads(str.encode(encode_variable).decode("utf-8"))))
        return encode_variable

    def parse_data(data):
        for key in data:
            print(key)
            print(data[key])

if __name__ == "__main__":
    server = Server()
    threading.Thread(target = server.handle_client, args = ('localhost', 8080)).start()
    threading.Thread(target = server.handle_lfd, args = ('Siyus-MBP-2.wv.cc.cmu.edu', 8082)).start()
    threading.Thread(target = server.handle_rec_checkpoint, args = ('Siyus-MBP-2.wv.cc.cmu.edu', 8086)).start()
    threading.Thread(target = server.handle_rm, args = ('Siyus-MBP-2.wv.cc.cmu.edu', 8084)).start()
   
