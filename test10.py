import time
import socket
import codecs
import numpy as np


def most_frequent(List):
    counter = 0
    num = List[0]
      
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            num = i
  
    return num


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(1)    # Wait for response from server
R = 1000            #Server sends R chars/sec
 
addr = ('149.171.36.192', 8190)
sr = '00000007' # 
# We choose Sr = 14 to avoid being exposed (50/4 = min message)
pr = '00000007'
datagram = sr + pr
data = codecs.decode(datagram, "hex_codec")
i=0
# For storing received msg
data_rec_list = []  # making a list to store data_rec with different submsg
full_data_rec_list = []
uid_list = []
submsg_list = []
final_msg = []
submsg_set = set()  # making a set to store different submsg received
eom_UID=[]
eom_list=[]
oct_id=[]
# ----- Receiving Messages -----
while i<3000:

    
    
    
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
    
    #apppending inf uid_list
    uid_list.append(int(submsg_id,16))
    submsg_list.append(submsg)
    final_msg.append(submsg)


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
  
    #if end_int==4:
        
        #eom_UID.append(int(submsg_id,16))
        
       ##########################################################
       
    ctrlD_substring = "\x04"

    if ctrlD_substring in submsg:
        eom_UID.append(int(submsg_id,16))
        eom_list.append(submsg)
    

    ######################################################################################
    data_rec_list_len = len(data_rec_list)
    submsg_set.add(submsg)
    submsg_len = len(submsg_set) # will increase if submsg added if different
   # print("The number of packets in this msg is: ",submsg_len) 
    # if there is a new submsg added to set, add the whole data_rec to list
    if data_rec_list_len != submsg_len: # add rec_data to list if received msg different
        data_rec_list.append(data_rec_msg)
        data_rec_list_len = submsg_len
        
    
    # increment pr
    i = i+1
        
        

s.close()
#print("Printing List of received data")
#print("[")
#for y in full_data_rec_list:
#    print(y)
#print("]")
#print("Printing List of received data")
#print("[")
#for w in data_rec_list:
#    print(w)
    
#print("]")

##############################################################
j=2
distance=[]
print(full_data_rec_list[-1])
while j< len(eom_UID):
    distance.append(eom_UID[j]-eom_UID[j-2])
    j=j+1
min_message_interval=most_frequent(distance)
packet_per_message=round(min_message_interval/interval_between_msg)

##############################################################
#Anthony rearranging


for k in range(len(uid_list)):
    uid_list[k] = uid_list[k]%packet_per_message
#print("Printing List of mod UID")
#print("[")
#for k in uid_list:
 #   print(k)
#print("]")

i = 0
while i < len(submsg_list):
    final_msg[uid_list[i]] = submsg_list[i]
    i+=1

res_msg2=final_msg[0:packet_per_message]
res_msg=final_msg[0:packet_per_message]
#print(eom_UID)
#print(eom_list)
#finding index with packet that includes Ctrl-D
i = 0
ctrlD_substring = "\x04"
while i<len(res_msg2):
    if ctrlD_substring in res_msg2[i]:
        break
    i+=1

ctrlD_index = i

print("Robert packet per message is",packet_per_message)
print("Anthony packet per message is",submsg_len)
# rearrange
j = 0
while j < len(res_msg):
    if (ctrlD_index+j+1) < len(res_msg):
        res_msg[j] = res_msg2[ctrlD_index + j + 1]
    elif (ctrlD_index+j+1) >= len(res_msg):
        res_msg[j] = res_msg2[ctrlD_index + j + 1 - len(res_msg)]
    j+=1

#print(res_msg2)
print("".join(res_msg))


#print(interval_between_msg)

print('23333333')
