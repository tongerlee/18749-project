import socket
import sys
import time

def start_server(sock):
    while True:
        print('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print('connecting from ', client_address)
            while True:
                data = connection.recv(1024)
                if data:
                    if data.decode("utf-8") == 'alive':
                        connection.sendall(data)
                    else:
                        print('received:' , time.ctime(), data)
                else:
                    print('no more data from', client_address)
                    break
        finally:
            connection.close()

if __name__=="__main__":
    # Bind the socket to the port
    # server_address = ('localhost', 8080)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (socket.gethostbyname('Siyus-MBP-2.wv.cc.cmu.edu'), 8082)
    print('starting up on ', server_address)
    sock.bind(server_address)
    sock.listen(3)

    start_server(sock)
