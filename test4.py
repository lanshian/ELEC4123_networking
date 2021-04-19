import time
import socket
import codecs
import numpy as np
import timeit
 

 
#message_len=100
s =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(1)
R = 1000;  
sleep_1000 = 0.05; 
Sr_1000 = 14; 

data = codecs.decode("0000001400000002", "hex_codec")
i=0
#data_rec=np.zeros(message_len)
print(data)
 

while i<30:

    time.sleep(0.7)

    addr = ('149.171.36.192', 8189)
   
    s.sendto(data,addr)
    print('data_sent')
    i=i+1;
    #start = timeit.timeit()
    data_rec, server =s.recvfrom(1024)
    #time.sleep(1)
    #end = timeit.timeit()
    #print(end - start)
    print('  RECEIVED:', data_rec)    
s.close()
print('2333333333')
