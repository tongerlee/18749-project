import json
import queue
import socket
import sys
import time
from datetime import datetime

def send_checkpoint():
    checkpoint = {}
    q1 = [1,2]
    checkpoint[1] = 3
    checkpoint[2] = 4
    mc1 = 7
    mc2 = 8
    q2 = [3,4]
    checkpoint = {mc1 : q1, mc2 : q2}
    print (checkpoint)
    js = json.dumps(checkpoint)
    print (js)
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('128.237.205.81', 10000)
    print(sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)
    try:
        iteration = 1

        # Send data
        while True:
            time.sleep(10)
            # now = datetime.now()
            # message = str(now) + "This is the message.  It will be repeated." + str(iteration)
            message = js
            print(sys.stderr, 'sending "%s"' % message)
            sock.sendall(str.encode(message))
            iteration += 1

        # Look for the response
        amount_received = 0
        amount_expected = len(message)
        while True:
            data = sock.recv(16)
            amount_received += len(data)
            print(sys.stderr, 'received "%s"' % data)

    finally:
        print(sys.stderr, 'closing socket')
        sock.close()
send_checkpoint()
