import socket
import sys

def start_server(sock):
    while True:
        print('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print('connecting from ', client_address)
            while True:
                data = connection.recv(1024)
                if data:
                    if data == 'alive?':
                        connection.sendall(data)
                    else:
                        print('received "%s %s"' %ctime() % data)
                else:
                    print('no more data from', client_address)
                    break
        finally:
            connection.close()

if __name__=="__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = (socket.gethostbyname('Siyus-MBP-2.wv.cc.cmu.edu'), 10000)
    print('starting up on ', server_address)
    sock.bind(server_address)
    sock.listen(5)

    start_server(sock)
