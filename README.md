# 18749-project

## Set-up Steps
### Replication Manager (Machine-1)
1. Change line 8, myhostname to your hostname.
2. Run command: python /18749-project/replica_manager/replicate_manager.py
3. Run on the same machine with GFD and clients.

### Global Fault Detector (Machine-1)
1. Change line 12, myhostname to your hostname
2. Run command: python /18749-project/global_fault_detector/global_fault_detector.py
3. Run on the same machine with RM and Clients

### Clients (Machine-1)
1. Take care of line 8, rm_ip before running the code
2. Run command: python /18749-project/client/client.py <client_id>
3. Run on the same machine with RM and GFD
4. Multiple clients can be launched with different <client_id> in the run command.

### Local Fault Detector (Machine-2/Machine-3/Machine-4)
1. Change line 12, gfd_ip_address to your the Machine-1 IP
2. Run command: python /18749-project/server/localfaultdetector/lfd.py
3. Run on the same machine with its server

### Replica/Server (Machine-2/Machine-3/Machine-4)
1. Change line 287, 289 and 290, change the hostname to yours
2. Change the IP address in line 129 to your IP address
2. Run command: python /18749-project/server/newversion.py
3. Run on the same machine with its LFD


## Active Replication Testing Step:
1. Launch the RM
2. Launch the GFD
3. Launch LFD-1 and Server-1
4. Launch LFD-2 and Server-2
5. Launch LFD-3 and Server-3

------ End of Fault-free Testing ------

------ Start Fault Testing ------

6. Kill one of the server
7. Wait for some time
8. Bring back the dead server
9. Clients and the other two server should work normally and consistently during these steps 
and the membership changes should be broadcasted to all clients and existing servers


