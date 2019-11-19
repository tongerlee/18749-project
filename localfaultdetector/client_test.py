import socket
import sys
import time
from multiprocessing import Process
import tcp_client 

heartbeat_message = "alive"
server_ip_address =  ('localhost', 10000)
alive_message = "Server is alive."
dead_message = "Server is dead."
gfd_ip_address =  ('localhost', 8000)

def heartbeat():
	while True:
		time.sleep(2)
		try:
			tcp_client.send_to(server_ip_address ,heartbeat_message,1)# wait 2 sec
			print('request sent')
		except:
			tcp_client.flag = 0# assume failed
		print (tcp_client.flag, tcp_client.msg)


heartbeat()
