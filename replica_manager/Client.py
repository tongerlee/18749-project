import socket
import sys
import time
from datetime import datetime


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print(sys.stderr, 'connecting to %s port %s' % server_address)
sock.connect(server_address)
try:
    iteration = 1

    # Send data
    while True:
        time.sleep(10)
        # now = datetime.now()
        # message = str(now) + "This is the message.  It will be repeated." + str(iteration)
        message = '1'
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