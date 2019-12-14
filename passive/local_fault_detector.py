import socket
import sys
import time
from datetime import datetime
from multiprocessing import Process
import tcp_client
import os

heartbeat_message = "alive"
server_ip_address = ('localhost', 8082)
alive_message = "Server is alive."
dead_message = "Server is dead."
gfd_ip_address = (os.environ.get('GFDIP'), 8000)


def heartbeat():
    
    while True:
        current_timestamp = str(datetime.now())
        time.sleep(2)
        try:
            tcp_client.send_to(server_ip_address, heartbeat_message, 1)  # wait 2 sec
        except:
            tcp_client.flag = 0  # assume failed
        # print (tcp_client.flag, tcp_client.msg)
        if tcp_client.flag == 1 and tcp_client.msg == heartbeat_message:  # get messsage
            print(current_timestamp + ' ' + alive_message)  # send message to gfd
            try:
                tcp_client.send_to(gfd_ip_address, alive_message, 0)
            except:
                pass
            tcp_client.flag = 0
        else:
            print(current_timestamp + ' ' + dead_message)
            try:
                tcp_client.send_to(gfd_ip_address, dead_message, 0)
            except:
                pass


heartbeat()
