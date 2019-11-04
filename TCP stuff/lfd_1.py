import socket
import sys
import time
from multiprocessing import Process
import tcp_server
import tcp_client 
import thread
ip_address = ('localhost', 10000)
heartbeat_message = "alive"
gfd_ip_address =  ('localhost', 8080)
dead_message = "Server is dead."

def heartbeat():
	while true:
		time.sleep(2)
		tcp_client.send_to(ip_address ,heartbeat_message)
		time.sleep(1)
		if flag[0] == 1 and msg[0] == heartbeat_message: #get messsage 
			print("Server is alive.")# send message to gfd
		else:
			print(dead_message)
			tcp_client.send_to(gfd_ip_address,dead_message)

thread.start_new_thread(heartbeat,("thread_1"))
thread.start_new_thread(tcp_server.listen_thread(ip_address,index=0),("thread_2"))