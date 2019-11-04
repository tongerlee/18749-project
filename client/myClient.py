import socket
import sys
import time
from datetime import datetime

#Create a TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect the socket to the port where the server is listening
server_address = ('128.237.160.194',10000)
print(sys.stderr,'connecting to %s port %s' % server_address)
sock.connect(server_address)
try:
	while True:
		message=sys.stdin.readline()
		print(sys.stderr,'sending "%s" ' % message)
		sock.sendall(str.encode(message))

finally:
	print(sys.stderr, 'closing socket')
	sock.close()
