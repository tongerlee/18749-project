import socket
import threading
import time
import json
import sys
from datetime import datetime
from queue import Queue
from collections import deque


class Server():
    def __init__(self):
        # initialize variable
        # listen for checkpoint request

        # self.clientMap = {"1": None, "2": None}
        self.q = Queue()
        self.lockReady = threading.Lock()
        self.isReady = False
        # number of messages processed for c1, c2 and queue of messages from c1,c2
        self.mc1 = 0
        self.mc2 = 0
        self.time1 = -1
        self.time2 = -1
        self.socket1 = None
        self.socket2 = None
        self.current_num_of_servers = 0

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
                data = client.recv(1024).decode('utf-8')
                parts = data.split(",")
                client_id = (int)(parts[0])
                time = (int)(parts[1])
                cnt = (int)(parts[2])
                if client_id == 1:
                    self.socket1 = client
                    print("got message from client 1")
                else:
                    self.socket2 = client
                    print("got message from client 2")

                print("Message put in queue")
                # if self.isReady:
                self.q.put((client_id, time, cnt))
            except:
                print("Dead during communicating with client")
                pass

    def handle_lfd(self, host, port):
        print("start local fault detector thread")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((socket.gethostbyname(host), port))

        sock.listen(5)
        print("listening at : ", host, port)

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
        print("listening at: ", host, port)

        while True:
            client, address = sock.accept()
            try:
                print('connecting from rm: ', address)
                data = client.recv(1024).decode('utf-8')
                # parse received data
                print("receive data from rm", data)
                new_servers = json.loads(data)['ip_list']
                num_of_servers = json.loads(data)['num_member']
                if self.current_num_of_servers != num_of_servers:
                    print('Membership change, current numbers: ' + str(num_of_servers))
                self.current_num_of_servers = num_of_servers
                if int(num_of_servers) == 1:
                    self.isReady = True
                    continue
                else:
                    self.isReady = False

                for new_server in new_servers:
                    new_ip = new_server[0]
                    if new_ip == '128.237.211.163':
                        continue
                    # prepare checkpoint
                    checkpoint = self.prepare_checkpoint()
                    print("checkpoint is ", checkpoint)
                    self.send_to_new_replica(checkpoint, new_ip, 8086)
                    self.lockReady.acquire()
                    self.isReady = True
                    self.lockReady.release()
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
        sock.listen()
        print("listening at : ", host, port)
        # print(sys.stderr, 'starting up on %s port %s' % server_address)

        # cnt = 0
        while True:
            # Wait for a connection
            connection, client_address = sock.accept()
            # cnt += 1
            # if cnt == 2:
            self.isReady = False

            time_1, time_2 = self.preprocess_queue()

            # Receive the data in small chunks and retransmit it
            # while True:
            raw_data = connection.recv(4096)  # ???
            current_timestamp = str(datetime.now())
            data = json.loads(raw_data.decode("utf-8"))
            self.mc1 = int(data["mc_1"])
            self.mc2 = int(data["mc_2"])
            self.time1 = int(data["time1"])
            self.time2 = int(data["time2"])
            received_q = data['queue']
            print("received_q is ==========================", received_q)

            for item in received_q:
                client_id = item[0]
                curr_time = item[1]
                if client_id == 1:
                    if time_1 is None or time_1 > curr_time:
                        self.mc1 += 1
                if client_id == 2:
                    if time_2 is None or time_2 > curr_time:
                        self.mc2 += 1

            self.isReady = True
            print("Checkpoint mc1= ", self.mc1, "mc2= ", self.mc2, "queue= ", self.q)
            print("Checkpoint received. I am ready")
            connection.close()
            break

    def preprocess_queue(self):
        cnt_1 = None
        cnt_2 = None
        for item in list(self.q.queue):
            client_id = int(item[0])
            curr_time = int(item[1])
            if client_id == 1:
                cnt_1 = curr_time
            else:
                cnt_2 = curr_time
        return cnt_1, cnt_2

    def send_to_new_replica(self, state, new_ip, port):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the new replica is listening
        print('Connecting to new replica at %s port %s' % (new_ip, port))
        try:
            sock.connect((new_ip, port))
            time.sleep(5)
            print("before send", str.encode(state))
            sock.sendall(str.encode(state))
        except socket.error as e:
            print("error is %d" % e)
            pass

        print('State sent to new replica at %s port %s' % (new_ip, port))
        sock.close()

    def prepare_checkpoint(self):
        print("all items in : *************************", list(self.q.queue))
        encode_variable = json.dumps({'mc_1': self.mc1, 'mc_2': self.mc2, 'time1': self.time1, 'time2': self.time2,
                                      'queue': list(self.q.queue)})
        print(str.encode(encode_variable))
        print(type(json.loads(str.encode(encode_variable).decode("utf-8"))))
        return encode_variable

    def process_client_request(self):
        print("start process_client_request thread")
        while True:
            # When the server is not busy sending checkpoint and the queue has messages
            self.lockReady.acquire()
            if self.isReady:
                self.lockReady.release()
                if not self.q.empty():
                    data = self.q.get()
                    if data[0] == 1:
                        if data[1] > self.time1:
                            self.time1 = data[1]
                            self.mc1 += data[2]
                            print("receive from client1, now seq num", self.mc1, self.time1)
                            if self.socket1 is not None:
                                self.socket1.sendall(str.encode(str(self.mc1)))
                                self.socket1.close()
                        else:
                            if self.socket1 is not None:
                                self.socket1.sendall(str.encode(str(self.mc1)))
                                self.socket1.close()
                    else:
                        if data[1] > self.time2:
                            self.time2 = data[1]
                            self.mc2 += data[2]
                            print("receive from client2, now seq num", self.mc2, self.time1)
                            if self.socket2 is not None:
                                self.socket2.sendall(str.encode(str(self.mc2)))
                                self.socket2.close()
                        else:
                            if self.socket2 is not None:
                                self.socket2.sendall(str.encode(str(self.mc2)))
                                self.socket2.close()

            else:
                self.lockReady.release()


if __name__ == "__main__":
    server = Server()
    threading.Thread(target=server.handle_client, args=('Jiatongs-MBP.wv.cc.cmu.edu', 8080)).start()
    threading.Thread(target=server.handle_lfd, args=('localhost', 8082)).start()
    threading.Thread(target=server.handle_rec_checkpoint, args=('Jiatongs-MBP.wv.cc.cmu.edu', 8086)).start()
    threading.Thread(target=server.handle_rm, args=('Jiatongs-MBP.wv.cc.cmu.edu', 8084)).start()
    threading.Thread(target=server.process_client_request).start()