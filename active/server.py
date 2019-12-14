import socket
import threading
import time
import json
import sys
from datetime import datetime
from queue import Queue
from collections import deque

MYHOSTNAME = socket.gethostname()
MYIP = socket.gethostbyname(MYHOSTNAME)


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
        self.checkpointReady = True
        self.thread_running = True

    def handle_client(self, host, port):
        print("start client thread")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((socket.gethostbyname(host), port))

        sock.listen(5)
        print("listening to : ", host, port)

        while self.thread_running:
            client, address = sock.accept()
            self.checkpointReady = False
            try:
                print('connecting from client: ', address)
                data = client.recv(1024).decode('utf-8')
                parts = data.split(",")
                client_id = (int)(parts[0])
                time = (int)(parts[1])
                cnt = (int)(parts[2])
                if client_id == 1:
                    self.socket1 = client
                    print("Got message from client 1")
                else:
                    self.socket2 = client
                    print("Got message from client 2")

                print("Message put in queue")
                # if self.isReady:
                self.q.put((client_id, time, cnt))
                self.checkpointReady = True
            except:
                # print("Dead during communicating with client")
                self.checkpointReady = True
                pass

        # print("Exception during processing data")
        # print("Is socket 1 exist?", self.socket1 is not None)
        # print("Is socket 2 exist?", self.socket2 is not None)
        if self.socket1 is not None:
            # print("Socket 1 exist, closing now")
            self.socket1.close()
        if self.socket2 is not None:
            # print("Socket 2 exist, closing now")
            self.socket1.close()

    def handle_lfd(self, host, port):
        print("start local fault detector thread")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((socket.gethostbyname(host), port))

        sock.listen(5)
        print("listening at : ", host, port)

        while self.thread_running:
            client, address = sock.accept()
            try:
                print('connecting from lfd: ', address)
                while self.thread_running:
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

        while self.thread_running:
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
                if self.current_num_of_servers < num_of_servers:
                    if int(num_of_servers) == 1:
                        self.isReady = True
                        continue
                    else:
                        self.isReady = False

                    for new_server in new_servers:
                        new_ip = new_server[0]
                        if new_ip == MYIP:
                            continue
                        # prepare checkpoint
                        while not self.checkpointReady:
                            continue
                        checkpoint = self.prepare_checkpoint()
                        print("Checkpoint is ", checkpoint)
                        self.send_to_new_replica(checkpoint, new_ip, 8086)
                        self.lockReady.acquire()
                        self.isReady = True
                        self.lockReady.release()
                self.current_num_of_servers = num_of_servers

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
        print("Before receiving checkpoint my queue is", list(self.q.queue))
        queue_received = False
        while self.thread_running:
            # Wait for a connection
            connection, client_address = sock.accept()
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
            if not queue_received and len(received_q) > 0:
                print("Add the queue content")
                queue_received = True
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
            # print("After this checkpoint mc1= ", self.mc1, "mc2= ", self.mc2, "queue= ", self.q)
            print("Checkpoint received. I am ready")
            connection.close()

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
            # print("before send", str.encode(state))
            sock.sendall(str.encode(state))
        except socket.error as e:
            print("error is %d" % e)
            pass

        # print('State sent to new replica at %s port %s' % (new_ip, port))
        sock.close()

    def prepare_checkpoint(self):
        # print("all items in : *************************", list(self.q.queue))
        encode_variable = json.dumps({'mc_1': self.mc1, 'mc_2': self.mc2, 'time1': self.time1, 'time2': self.time2,
                                      'queue': list(self.q.queue)})
        # print(str.encode(encode_variable))
        # print(type(json.loads(str.encode(encode_variable).decode("utf-8"))))
        return encode_variable

    def process_client_request(self):
        try:
            print("start process_client_request thread")
            while self.thread_running:
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
                                print('send--------------client1--------------', str(self.mc1))
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
                                print('send--------------client2--------------', str(self.mc2))
                                if self.socket2 is not None:
                                    self.socket2.sendall(str.encode(str(self.mc2)))
                                    self.socket2.close()
                            else:
                                if self.socket2 is not None:
                                    self.socket2.sendall(str.encode(str(self.mc2)))
                                    self.socket2.close()

                else:
                    self.lockReady.release()
        except:
            # print("Exception during processing data")
            # print("Is socket 1 exist?", self.socket1 is not None)
            # print("Is socket 2 exist?", self.socket2 is not None)
            if self.socket1 is not None:
                self.socket1.close()
            if self.socket2 is not None:
                self.socket2.close()


if __name__ == "__main__":
    server = Server()
    threads = []
    try:
        threads.append(threading.Thread(target=server.handle_client, args=(MYHOSTNAME, 8080)))
        threads.append(threading.Thread(target=server.handle_lfd, args=('localhost', 8082)))
        threads.append(threading.Thread(target=server.handle_rec_checkpoint, args=(MYHOSTNAME, 8086)))
        threads.append(threading.Thread(target=server.handle_rm, args=(MYHOSTNAME, 8084)))
        threads.append(threading.Thread(target=server.process_client_request))
        for eachThread in threads:
            eachThread.start()
        while server.thread_running:
            continue
    except KeyboardInterrupt:
        server.thread_running = False

        if server.socket1 is not None:
            server.socket1.close()
        if server.socket2 is not None:
            server.socket2.close()
        for eachThread in threads:
            eachThread.join()
        sys.exit()