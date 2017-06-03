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
        self.ck_size=0
        self.resend=0
        self.seq = 0
        self.no_pkts = 0
        self.x_percent = 1
        self.corruption = False
        self.timeout = 0.03
        self.gpkt = ""
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

    def checksum(self, pkt):
        sum = 0
        data_hex = binascii.hexlify(pkt)
        for i in data_hex:
            sum = sum + int(i,16)
            #sum = str(sum)
        #print "sum is "+sum
        return (sum)
            
    def make_packets(self,data):
        check_sum=self.checksum(data)
        self.ck_size = len(str(check_sum))
        #print "Sent checksum"
        pkt =str(self.seq)+str(check_sum)+data
        return(pkt)
	
    def time_out(self):
        self.resend = self.resend+1
        self.send_data(self.gpkt)
	return (self.resend)
    
    def send_data(self, x):
        self.send_msg("Checksum")
        self.send_msg(str(self.ck_size))
        self.send_msg("packet size")
        self.send_msg(str(len(x)))
        self.send_msg(x)
        self.ack_recv=0
	finish = False
        start = time.time()
        while(finish == False):
            time_diff = time.time()-start
            #print "waiting"
            #print "time_diff is " + str(time_diff)
            if(time_diff>self.timeout):
                print "Time out!"
                break
            if(self.ack_recv == 0):
                ack, clientAddress = self.clientSocket.recvfrom(2048)
                if(ack):
			self.ack_recv =1
                    	ack = int(ack)
                    	#print "ack " + str(ack)
                    	if(int(self.option) == 2 or int(self.option) == 4):
				#print "I am at ack"
                        	lim = 100/int(self.x_percent)
                        	if(random.randint(0,lim)==1):
                            		ack = ~ack
                            		finish=False
			if(self.seq == ack):
				finish=True
                    #self.count = self.count +1
                    #print "count is "+ str(self.count)
                            	if (self.seq == 0):
                                	self.seq = 1
                            	else:
                                	self.seq = 0
        if(finish == False):
        	t = self.time_out()
	return 0
    

    def serverSend(self):
        print "Choose 1 options out of 5. Enter 1/2/3/4/5"
        print "1. No Error\n2. Ack Error\n3. Data Error\n4. ACK Loss\n5. Data Loss"
        self.option = raw_input('--> ')
        self.send_msg("option")
        self.send_msg(str(self.option))
        count = 0
        if(int(self.option) != 1):
            print "Enter the % of corruption or loss"
            self.x_percent = raw_input("--> ")
    	if(int(self.option) == 3 or int(self.option) == 5):
            self.send_msg(self.x_percent)
        with open("high snow.jpg","rb") as file1:
        	str1 = base64.b64encode(file1.read())
        	pkts = self.make_chunks(str1)
        	while 1:
                	print "Sending pkts now.."
            		start_time = time.time()
            		for x in pkts:
				count = count + 1
                            	#print "count " + str(count)
                       		self.gpkt= self.make_packets(x)
                       		self.send_data(self.gpkt)
				if(self.no_pkts==count):
					self.send_msg("all ok")
               		file1.close()
                	end_time = time.time()
        		print ("Time taken is %s" %(end_time-start_time))
                	break

obj1 = server()
obj1.serverSend()
