import socket
import sys
import time


def send_to(IP , message, wait):
    global msg
    global flag
    msg = ''
    flag = 0
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
#    server_address = ('localhost', 10000)
    #print ( 'connecting to ', IP)
    sock.connect(IP)

    try:
        sock.sendall(message.encode())
        # Look for the response
        amount_received = 0
        amount_expected = len(message) 
        count = 0
        while amount_received < amount_expected and count<2 and wait ==1:
            print (count)
            count+=1
            time.sleep(1)
            data = sock.recv(16)
            if data:
                flag = 1
                msg += data.decode("utf-8") 
            amount_received += len(data)
            #print ('received ', data)

    finally:
        #print ('closing socket')
        sock.close()
