import socket
import sys
import time
from threading import Thread

timeoutflag = 0

def timeout(sleeptime):
    time.sleep(sleeptime)
    timeoutflag =1

def send_to(IP , message, waittime):
    global msg
    global flag
    msg = ''
    flag = 0
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(IP)

    try:
        sock.sendall(message.encode())
        # Look for the response
        amount_received = 0
        amount_expected = len(message)
        if waittime >0:
            timeoutflag =0
            Thread(target=timeout, args=[waittime]).start()
        else:
            timeoutflag=1
        while amount_received < amount_expected and timeoutflag ==0:
            data = sock.recv(1024)
            if data:
                flag = 1
                msg += data.decode("utf-8") 
            amount_received += len(data)
    finally:
        sock.close()
