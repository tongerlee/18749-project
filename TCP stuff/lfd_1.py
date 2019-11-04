import socket
import sys
import time
from multiprocessing import Process
import tcp_server
import tcp_client 
import _thread
ip_address = ('localhost', 10000)
heartbeat_message = "alive"
gfd_ip_address =  ('localhost', 8092)
dead_message = "Server is dead."



def heartbeat():
	while True:
		time.sleep(2)
		tcp_client.send_to(gfd_ip_address ,heartbeat_message)
		time.sleep(2)
		if tcp_server.flag[0] == 1 and tcp_server.msg[0] == heartbeat_message: #get messsage 
			print("Server is alive.")# send message to gfd
		else:
			print(dead_message)
			#tcp_client.send_to(gfd_ip_address,dead_message)

_thread.start_new_thread(heartbeat(),tuple("thread_1"))
_thread.start_new_thread(tcp_server.listen_thread(ip_address,0),tuple("thread_2"))