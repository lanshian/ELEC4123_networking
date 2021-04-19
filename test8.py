import time
import socket
import codecs
import numpy as np

# To run server:
# ssh np1@149.171.36.192
# /usr/local/bin/4123-server -file message.txt -port 8189 -address 149.171.36.192 -http_start 300 -verbose
# ----- Connecting to server -----
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(1)    # Wait for response from server
R = 1000            #Server sends R chars/sec
 
addr = ('149.171.36.192', 8189)
sr = '00000007' # sr = 14 (dec)= e (hex)
# We choose Sr = 14 to avoid being exposed (50/4 = min message)
pr = '00000007'
datagram = sr + pr
data = codecs.decode(datagram, "hex_codec")
i=0
# For storing received msg
data_rec_list = []  # making a list to store data_rec with different submsg
full_data_rec_list = []
submsg_set = set()  # making a set to store different submsg received
eom_UID=[]
# ----- Receiving Messages -----
while i<3000:
    try:
        
    
        
        data = codecs.decode(datagram, "hex_codec")
        #print('Data Sent:', data)
        s.sendto(data,addr)
        data_rec, server =s.recvfrom(1024)
 
        data_rec = data_rec.hex()  # this is required to decode byte packet properly
        #print("Data received: {}".format(data_rec))
        pr_rec = data_rec[0:8]
        submsg_id = data_rec[8:16]
        submsg = bytearray.fromhex(data_rec[16:]).decode()
        #print("Pr: {} | ID: {} | Submsg: {}".format(pr_rec, submsg_id, submsg)) 

        data_rec_msg = [pr_rec, submsg_id, submsg]  # combining decoded received msg
        full_data_rec_list.append(data_rec_msg)
        
        #reformat our end charactor into int and compare with 4
        #########################################################################
        end_msg_needed=format(ord(submsg[-1]), "x")
        end_char="0x"+ end_msg_needed
        end_int=int(end_char,0)
        if i==10:
            pre_msgID=int(submsg_id,16)
        if i==12:
            interval_between_msg=abs(pre_msgID-int(submsg_id,16))
      #  if end_msg_needed ==
      
        if end_int==4:
            
            eom_UID.append(int(submsg_id,16))
           
        ######################################################################################
        data_rec_list_len = len(data_rec_list)
        submsg_set.add(submsg)
        submsg_len = len(submsg_set) # will increase if submsg added if different
        print("The number of packets in this msg is: ",submsg_len) 
        # if there is a new submsg added to set, add the whole data_rec to list
        if data_rec_list_len != submsg_len: # add rec_data to list if received msg different
            data_rec_list.append(data_rec_msg)
            data_rec_list_len = submsg_len
            
        
        # increment pr
        i = i+1
        print('\n')

       

        
    except:
        print('error')
s.close()
print("Printing List of received data")
print("[")
for y in full_data_rec_list:
    print(y)
print("]")
print("Printing List of received data")
print("[")
for w in data_rec_list:
    print(w)
    
print("]")

##############################################################
j=2
distance=[]
print(full_data_rec_list[-1])
while j< len(eom_UID):
    distance.append(eom_UID[j]-eom_UID[j-2])
    j=j+1
min_message_interval=min(distance)

packet_per_message=min_message_interval/interval_between_msg

print("packet per message is",packet_per_message)
print('23333333')


######################################################################
