# function of print (timestamp: n members)
# list of replica: n = len(list)
# receive message from Global Fault detector
import socket
import sys
from datetime import datetime

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = (socket.gethostbyname("Jiatongs-MBP.wv.cc.cmu.edu"), 10000)
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
        data = connection.recv(16)
        current_timestamp = str(datetime.now())
        # print(sys.stderr, current_timestamp + ': ' + str(data) + ' members')
        print("%s: %s members" % (current_timestamp, data.decode("utf-8")))
        if not data:
            print ("No receive data from GFD")
            # sleep(10)
            break