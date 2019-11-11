import socket
import threading
import time

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = socket.gethostbyname(host)
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            threading.Thread(target = self.listenToClient, args = (client, address)).start()

    def listenToClient(self, client, address):
        size = 1024
        try:
            print('connecting from ', address)
            while True:
                data = client.recv(size)
                if data:
                    if data.decode("utf-8") == 'alive':
                        client.sendall(data)
                    else:
                        print(time.ctime(), data)
                else:
                    print('no more data from', client_address)
                    break
        finally:
            client.close()

if __name__ == "__main__":
    # while True:
    #     port_num = input("Port? ")
    #     try:
    #         port_num = int(port_num)
    #         break
    #     except ValueError:
    #         pass

    ThreadedServer('localhost', 8080).listen()
    # ThreadedServer(socket.gethostbyname('Siyus-MBP-2.wv.cc.cmu.edu'), 8082).listen()
    ThreadedServer('Siyus-MBP-2.wv.cc.cmu.edu', 8082).listen()
