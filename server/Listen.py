import json
import socket
import sys
from datetime import datetime
from queue import Queue


def init():
    # initialize variable
    # listen for checkpoint request
    mc1, mc2 = 0, 0
    q1, q2 = Queue(), Queue()


def parse_data(data):
    for key in data:
        print(key)
        print(data[key])


def rec_checkpoint():
    # send ip, port to RM
    """

    :param checkpoint: JSON
    :return:
    """
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = (socket.gethostbyname("chenweideMBP.wv.cc.cmu.edu"), 10000)
    # server_address = (addr, port)
    # server_address = ('128.237.198.254', 8000)
    print(sys.stderr, 'starting up on %s port %s' % server_address)
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print(sys.stderr, 'waiting for a connection')
        connection, client_address = sock.accept()
        # try:
        print(sys.stderr, 'connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            raw_data = connection.recv(4096)  #???
            current_timestamp = str(datetime.now())
            # print(sys.stderr, current_timestamp + ': ' + str(data) + ' members')
            #print("%s: %s members" % (current_timestamp, data.decode("utf-8")))
            print(raw_data)
            data = json.loads(raw_data)
            if not data:
                print ("No receive data from Server")
                break
            print(parse_data(data))


def rec_rm(data):
    # expect {id: (ip,port)}, membership=len(dict)
    # if membership=1 only init; else init + rec_checkpoint
    membership = len(data)
    pass


if __name__ == "__main__":
    init()
    rec_checkpoint()

