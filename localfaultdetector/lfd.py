import socket
import sys
import time
from multiprocessing import Process
import tcp_server
import tcp_client 
import _thread
my_ip_address = ('localhost', 8888)
heartbeat_message = "alive"
server_ip_address =  ('localhost', 8080)
alive_message = "Server is alive."
dead_message = "Server is dead."
gfd_ip_address =  ('128.237.198.254', 8000)

def heartbeat():
	while True:
		time.sleep(2)
		try:
			tcp_client.send_to(server_ip_address ,heartbeat_message,1)# wait 2 sec
		except:
			pass
		if tcp_client.flag == 1 and tcp_client.msg == heartbeat_message: #get messsage 
			print(alive_message)# send message to gfd
			try:
				tcp_client.send_to(gfd_ip_address,alive_message,0)
			except:
				pass
			tcp_client.flag = 0
		else:
			print(dead_message)
			try:
				tcp_client.send_to(gfd_ip_address,dead_message,0)
				print ('msg sent')
			except:
				pass

_thread.start_new_thread(heartbeat(),tuple("thread_1"))
_thread.start_new_thread(tcp_server.listen_thread(my_ip_addressip_address,0),tuple("thread_2"))
