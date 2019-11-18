import socket
import sys
import time
from threading import Thread

def send_to(IP , message, waittime):
    global msg
    global flag
    msg = ''
    flag = 0
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(IP)
    sock.settimeout(waittime)
    try:
        sock.sendall(message.encode())
        data = sock.recv(1024)
        if data:
            flag = 1
            msg = data.decode("utf-8") 
    finally:
        sock.close()
