import base64
import random
import sys
import time
import binascii
from socket import *

class server():
    def __init__(self):
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverName = "localhost"
        self.serverRPort = 7380
        self.serverSPort = 7356
        self.clientSocket.bind(('', self.serverRPort))
        self.chunk_size = 1024
        self.pkts=[]
        self.ck_size=0
        self.sq_size=0
        self.resend=0
        self.send_seq = 0
        self.exptd_seq = 0
        self.recv_seq = 0
        self.start=0
        self.base=0
        self.ack=0
	self.no_acks=0
        self.no_pkts = 0
        self.x_percent = 1
        self.N=0
        self.corruption = False
        self.timeout = 1
        self.ack_recv = 0
	self.option = ""
    
    def send_msg(self, msg):
        self.clientSocket.sendto(msg,(self.serverName, self.serverSPort))
    	time.sleep(.001)
    
    def make_chunks(self,data):
        file_size = len(data)
        self.no_pkts = file_size/self.chunk_size
        rem1 = file_size % self.chunk_size
        if(rem1):
            self.no_pkts = self.no_pkts+1
        print self.no_pkts
        pkt = []
        for i in range (0,self.no_pkts):
            pkt.append(data[i*self.chunk_size:(i+1)*self.chunk_size])
            #print i
        print "starting.."
        self.send_msg("no of packets")
        print "sending file size"
        self.send_msg(str(self.no_pkts))
        self.send_msg("chunk size")
        self.send_msg(str(self.chunk_size))
        return pkt

    def start_timer(self):
        self.start = time.time()
        return 0

    def checksum(self, pkt):
        sum = 0
        data_hex = binascii.hexlify(pkt)
        for i in data_hex:
            sum = sum + int(i,16)
        sum = str(sum)
        #print "sum is "+ sum
        return (sum)
            
    def make_packets(self,data):
        check_sum=self.checksum(data)
        self.ck_size = len(str(check_sum))
        #print "checksum size is "+ str(self.ck_size)
        self.sq_size = len(str(self.send_seq))
        pkt =str(self.send_seq)+str(check_sum)+data
        return(pkt)
	
    def time_out(self):
        resend = self.send_seq - self.base
        self.start_timer()
        #print "starting timer at resending"
	#print "resending packets "+ str(resend)
	self.send_seq = self.base
        for i in range(resend):
            self.send_data(self.pkts[self.base+i])
	    self.send_seq += 1
            #print "resending packet no "+ str((self.base +i))
        return (resend)
    
    def send_data(self, x):
        gpkt= self.make_packets(x)
        self.send_msg("Checksum")
        self.send_msg(str(self.ck_size))
        #print "Checksum size is " + str(self.ck_size)
        self.send_msg("seq size")
        self.send_msg(str(self.sq_size))
        #print "sequence size is " + str(self.sq_size)
        self.send_msg("packet size")
        self.send_msg(str(len(gpkt)))
        #print "packet size is " + str(len(gpkt))
        self.send_msg(gpkt)
        if(self.base==self.send_seq):
            self.start_timer()
            #print "starting timer at first msg of window"
        return 0
        
    def receive(self):
                self.ack_recv=0
                no_acks = self.N
                #print "Recever is called"
		while(1):
                	time_diff = time.time()-self.start
            		if(time_diff>self.timeout):
                		print "Time out!"
                    		t = self.time_out()
                    		self.ack_recv=0
                    		self.no_acks = t
                	if(self.ack_recv < self.no_acks):
				drop=0
                        	self.recv_seq, clientAddress = self.clientSocket.recvfrom(2048)
                        	if(self.recv_seq):
                                	self.ack_recv +=1
                                	self.recv_seq = int(self.recv_seq)
                                	print "ack " + str(self.recv_seq)
                                	if(int(self.option) == 2 or int(self.option) == 4):
                                    		#print "I am at ack corruption"
                                    		lim = 100/int(self.x_percent)
                                    		if(random.randint(0,lim)==1):
                                        		self.recv_seq = self.recv_seq-1
							if(int(self.option)==4):
								drop=1
                                        		#print "corrupted ack is " + str(self.recv_seq)
					if(drop==0):
                                		if(self.exptd_seq == self.recv_seq):
                                    			#print "True ack received"
                                    			#print "sequence received "+str(self.recv_seq)
                                    			self.base +=1
                                    			self.exptd_seq +=1
                                    			#print "expected sequence is "+ str(self.exptd_seq)
                                    			if(self.base == self.send_seq):
								print "Yippeee.."
                                        			break
                                    			else:
                                        			self.start_timer()
                                                	#print "Staring timer at receiver"
        	return 0

    def serverSend(self):
        print "Choose 1 options out of 5. Enter 1/2/3/4/5"
        print "1. No Error\n2. Ack Error\n3. Data Error\n4. ACK Loss\n5. Data Loss"
        self.option = raw_input('--> ')
        self.send_msg("option")
        self.send_msg(str(self.option))
        allsent = 0
        if(int(self.option) != 1):
            print "Enter the % of corruption or loss"
            self.x_percent = raw_input("--> ")
    	if(int(self.option) == 3 or int(self.option) == 5):
            self.send_msg(self.x_percent)
        print "Enter the window size (1, 2, 5, 10, 20, and 50)"
        self.N = raw_input('--> ')
        self.send_msg("window size")
        self.send_msg(self.N)
	self.N = int(self.N)
        with open("high snow.jpg","rb") as file1:
        	str1 = base64.b64encode(file1.read())
        	self.pkts = self.make_chunks(str1)
        	while 1:
                	print "Sending pkts now.."
            		start_time = time.time()
                    	for x in range(0,self.no_pkts,self.N):
				#print "value of x is "+ str(x)
				for y in range(self.N):
					#print "value of y is "+str(y)
					if(x+y<self.no_pkts):
						self.send_data(self.pkts[x+y])
						#print "packet sent "+ str(self.send_seq)
                                            	self.send_seq += 1
                                        else:
                                            	#print "all pkts sent"
						y=y-1
						break
				self.no_acks = y+1
				self.receive()
                    	if(self.send_seq==self.no_pkts):
				self.send_msg("all ok")
                                #print "sent all ok the receiver"
               		file1.close()
                	end_time = time.time()
                    	print ("Time taken is %s" %(end_time-start_time))
                	break

obj1 = server()
obj1.serverSend()
