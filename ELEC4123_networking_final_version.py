import random
import functools
import time
import socket
import codecs
import numpy as np
import math
import select
import time
import requests
def factors(n):
    return set(functools.reduce(list.__add__, ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))  
    
class TestServer():
    def __init__(self):
        f = open('message.txt', 'r')
        message = f.read()
        message += '\x04'
        self.fullmsg = message
        f.close()
        splitted_message = []
        i = 0
        while i < len(message):
            l = random.randint(4,20)
            splitted_message.append(message[i:i+l])
            i += l
        self.message = splitted_message
        self.total = len(self.message)
        self.pos = 0
        self.id = random.randint(0,1000)
        print(f'Real packets in message: {self.total}')
 
    def get_message(self):
        # simulate server, choose a random number from 7-20 to iterate internal pos
        ran = random.randint(7,9)
        self.pos = (self.pos + ran) % self.total
        self.id += ran
        return (self.id, self.message[self.pos % self.total])
 
class RealServer():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)    # 0 = Do not wait for response from server
        port = 8189
        self.addrmsg = ('149.171.36.192', port)
        self.addrhttp = ('149.171.36.192', port + 1)
        self.url = 'http://' + self.addrhttp[0] + ':' + str(self.addrhttp[1])
        self.pr = '00000420' # set to whatever
    def get_message(self):
        try:
            sr = format(random.randint(7, 9), 'x').zfill(8)     # Randomly sample every 7, 8, or 9th packet
            datagram = sr + self.pr
            data = codecs.decode(datagram, "hex_codec")
            self.sock.sendto(data,self.addrmsg)
            ready = select.select([self.sock], [], [], 10)   # timeout
            if ready[0]:
                data_rec = self.sock.recv(1024)
                data_rec = data_rec.hex()  # this is required to decode byte packet properly
                pr_rec = data_rec[0:8]
                submsg_id = data_rec[8:16]
                submsg = bytearray.fromhex(data_rec[16:]).decode()
                #print("Pr: {} | ID: {} | Submsg: {} | Length: {}".format(pr_rec, submsg_id, submsg, len(submsg))) 
                data_rec_msg = [int(submsg_id, 16), submsg]  # combining decoded received msg
                return data_rec_msg
            else:
                print('Timed out')
        except Exception as e:
            print(f'Error: {e}')
            self.sock.close()
 
LOCAL_TESTING = False       # To use Test server, change to True
start = time.time()     # Timer
if LOCAL_TESTING == True:   # Real server: 4123-server | Test server: mimick server behaviour on local machine
    s = TestServer()
else:
    s = RealServer()

num_messages = 0
http_response = 200
while http_response == 200 or http_response == 406:  # If message sent was successful (200) or incorrect (406), run code anyway
    allPackets = []                 # Save incoming packets
    allPacketsNoDupes = set()       # Save incoming non duplicate packets
    if LOCAL_TESTING == True:
        EOF_COUNT = 2
    else:
        EOF_COUNT = 4   # Because of duplicates packets being sent back to us, this is still EOF_COUNT = 4
    EOFs = []           # Save all UIDs and submessages of EOF packets
    eof_string = None
 
    # ----- Receiving Messages -----
 
    throwaway = 10  # Number of packets to throwaway
    t = 0           # Index for how many packets thrown away
    while len(EOFs) < EOF_COUNT:    # While less than 2 EOF packets are found:
        ret = s.get_message()       # Send UDP datagram request to server, and receive it here with format: [UID, ]
        if t < throwaway and num_messages > 0:      # Discard first 10 packets of every subsequent message to avoid receiving old message packets in new message
            t += 1
        else:
            if ret is None:     # Catch error
                print('Returned packet was none!')
                quit()
            if "\x04" in ret[1]:    # If packet has an EOF char:
                print(f"EOF found at {ret[0]}")
                EOFs.append(ret[0])             # Save uID of EOF packets
                eof_string = ret[1]             # Save most recently sampled EOF submessage in this variable, to put in final[]
            allPackets.append([ret[0], ret[1]]) # Save packet [UID, submessage]
            allPacketsNoDupes.add(ret[1])       # Save packet submessage if unique (set)
    # --- Find all possible lengths ---
    diffs = []  # Store number of packets between EOFs
    i = 1
    while i < len(EOFs):
        diffs.append(EOFs[i]-EOFs[i-1]) # Number of packets between EOFs
        i += 1
    # Ignore common factor if EOF_COUNT <= 4
    #xs = functools.reduce(lambda x,y: math.gcd(x,y), diffs) # Greatest common divisor to find possible length values
    #print(f'GCD: {xs}')
 
    xs = EOFs[2] - EOFs[0]
    # Assume xs is wrong because we miss sampling an EOF, so try to take factors of xs in case we chose a multiple
   
    
    final_xs = [e for e in list(factors(xs)) if e >= len(allPacketsNoDupes) and e <= 1250]    # Filter xs's factors with a lower boundary of number of unique packets and upper boundary of 1250
    final = [[None]*(l-1) +[eof_string]  for l in final_xs] # Create array with sizes of possible lengths [l][None, None, ..., None, "..x04"]
    consider_f = [True for f in final]      # Initially all message lengths are possible [True, True, ... , True]
 
    print(f"final X's: {final_xs}\nconsider_f: {consider_f}")
 
    EOF_index = EOFs[-1]        # Grab UID of last EOF
    print(f'EOF index {EOF_index}')
    # --- Fill in arrays of possible lengths ---
    # 
    checkedAllPackets = False
    allPacketsIter = iter(allPackets)
    success = False
    print('CHECKING PREVIOUSLY SAVED PACKETS...')
    while not success:
        # First we look at all the packets we have saved so far to put into final[]
        if checkedAllPackets == False:
            try:
                m = next(allPacketsIter)    # iterator to iterate through allPackets
            except:
                checkedAllPackets = True
                print('REQUESTING AND CHECKING NEW PACKETS...')
                m = s.get_message()
        else:
            m = s.get_message()
        #print(f"final X's: {final_xs}\nfinal lens: {[len(f) for f in final]}\nconsider_f: {consider_f}")
        for i in range(len(final)):
            if consider_f[i]:
                temp_m = m[0]       # Packet UID
                while temp_m < EOF_index:
                    temp_m += final_xs[i]     # for all packet
                index = (temp_m-EOF_index-1) % final_xs[i]    # Find UID differnece between EOF and current packet. Mod with possible length
                if final[i][index]:
                    if final[i][index] == m[1]:             # If message existing in final[] is same as retrieved msg, continue
                        continue
                    else:
                        # ignore this case
                        print(f'{i} index false!')
                        consider_f[i] = False               # If message in final[] is not same as retrieved msg, this length cannot be valid
                        #break
                else:
                    final[i][index] = m[1]                  # If no message existing in final [] (i.e. None), insert msg
        for i in range(len(final)):
            if consider_f[i] and None not in final[i]:      # If a final[] array is filled and the length was not invalidated, must be the correct length
                print("I'm done")
                #print("".join(final[i]))
                print(f'Final length: {len(final[i])}')
                if LOCAL_TESTING == True:
                    if (len(final[i]) == s.total and "".join(final[i]) == s.fullmsg):
                        print('SUCCESS')
                    else:
                        print('FAIL')
                    http_response = 205
                success = True
                end = time.time()
                final_msg = "".join(final[i])   # Convert array to string
                print(f'MESSAGE SENT BELOW:\n{final_msg}')
                print(f'Time taken: {end - start}')
                break
        if True not in consider_f:      # If for some reason no lengths are valid, rerun code
            print("All possible lengths seem invalid?")
            end = time.time()
            print('BROKEN MESSAGE:\n')
            for k in final:
                print(f'{k}')
            print(f'Time taken: {end - start}')
            break
 
    if LOCAL_TESTING == False:
        x = requests.post(s.url, data = final_msg ,headers={'Connection':'close'})
        print(f'Status code: {x.status_code}')
        http_response = x.status_code
        num_messages += 1
        print(f'Messages sent: {num_messages}')
        if http_response == 205:
            print("All messages authenticated")
            quit()