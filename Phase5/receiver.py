from socket import *
import sys
import time
import base64
import binascii
import random

class client():
    def __init__(self):
        self.serverRPort = 7356
        self.serverSPort = 7380
        self.serverName = "localhost"
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind(('', self.serverRPort))
        self.exptd_seq=0
        self.recv_ACK=0
        self.drop=1
	self.option=0
        self.ok_packet=-1
        self.sent=0
        self.allok =1
        self.allok1 = 1
        self.check_sum=0
        self.corruption = False
        self.x_percent =1
        print "Server is ready to recieve!"
    
    def checksum(self, data):
	if(self.allok and self.drop):
        	sum = 0
        	#print "I am at checksome"
        	data_hex = binascii.hexlify(data)
        	for i in data_hex:
            		sum = sum + int(i,16)
        	#print "checksum is "+str(sum)
        	if(sum != self.check_sum):
            		self.allok1 =0
            		#print "Wrong Checksum"
            		self.exptd_seq = self.exptd_seq -1
            		#print "Correctly Received "+str(self.recv_ACK)
	    		#print "Changed Expected sequence "+str(self.exptd_seq)
        	else:
            		self.allok1 = 1
	    		#print "everything ok at checksum"
        return 0
    
    def make_corrupt(self,data):
        lim = 100/int(self.x_percent)
        if(random.randint(0,lim) == 1):
            if(int(self.option)==5):
                self.drop=0
                self.allok1=0
		self.exptd_seq = self.exptd_seq -1
                #print "I am droping the packet "+ str(self.recv_ACK)
            else:
                data="377485854985"
        return(data)
        
    def resend_ACK(self):
	self.send_msg(str(self.recv_ACK))
	#print "resending the ACK "+str(self.recv_ACK)
	self.sent=1
	return 0
	
    def extract_header(self, pkt,ck_size, sq_size):
        #print "I am extracting"
	self.sent=0
        self.recv_ACK=int(pkt[0:sq_size])
        #print "Received ACK "+str(self.recv_ACK)
        if(self.recv_ACK != self.exptd_seq):
            self.allok=0
            #print "Droping the packet " + str(self.recv_ACK)
	    if(self.recv_ACK<self.exptd_seq):
		self.resend_ACK()
        else:
            self.allok=1
            self.exptd_seq = self.exptd_seq +1
	    #print "Expected sequnece "+ str(self.exptd_seq)
            #print "all ok"
        self.check_sum = int(pkt[sq_size:(sq_size+ck_size)])
        #print "checksum received "+ str(self.check_sum)
        data = pkt[(sq_size+ck_size):]
        if (self.corruption and self.allok):
            data = self.make_corrupt(data)
        #print "length of data is " + str(len(data))
        return(data)

    def send_msg(self, msg):
        self.serverSocket.sendto(msg,(self.serverName, self.serverSPort))
    	time.sleep(.001)



    def clientRecv(self):
            msg, clientAddress = self.serverSocket.recvfrom(2048)
            print msg
            if (msg == "option"):
                self.option, clientAddress = self.serverSocket.recvfrom(2048)
                print self.option
            if(int(self.option)==3 or int(self.option)==5):
                self.x_percent, clientAddress = self.serverSocket.recvfrom(2048)
                self.corruption = True
            msg, clientAddress = self.serverSocket.recvfrom(2048)
            print msg
            if (msg == "window size"):
                self.window_size, clientAddress = self.serverSocket.recvfrom(2048)
                print self.window_size
            self.window_size= int(self.window_size)

            msg1, clientAddress = self.serverSocket.recvfrom(2048)
            print msg1
            if (msg1 == "no of packets"):
                    no_pkts, clientAddress = self.serverSocket.recvfrom(2048)
                    print no_pkts
            msg2, clientAddress = self.serverSocket.recvfrom(2048)
            print msg2
            if (msg2 == "chunk size"):
                chunk_size, clientAddress = self.serverSocket.recvfrom(2048)
                print chunk_size
            no_pkts = int(no_pkts)
            chunk_size = int(chunk_size)
            count = 0
            fin_data =[]
            while 1:
                msg3, clientAddress = self.serverSocket.recvfrom(2048)
                if (msg3 == "Checksum"):
                    ck_size, clientAddress = self.serverSocket.recvfrom(2048)
                    #print "checksum size is " + ck_size
                    ck_size = int(ck_size)
                
                msg4, clientAddress = self.serverSocket.recvfrom(2048)
                if (msg4 == "seq size"):
                    sq_size, clientAddress = self.serverSocket.recvfrom(2048)
                    sq_size = int(sq_size)
                    #print "Sequence size is " +str(sq_size)
                
                msg5, clientAddress = self.serverSocket.recvfrom(2048)
                if (msg5 == "packet size"):
                    pkt_size, clientAddress = self.serverSocket.recvfrom(2048)
                    #print "Packet size is " + pkt_size
                    pkt_size = int(pkt_size)
                   
                pkt, addr = self.serverSocket.recvfrom(pkt_size)
                if(pkt):
                    pkt = self.extract_header(pkt,ck_size,sq_size)
                    self.checksum(pkt)
                    self.drop=1
                    #self.send_msg(str(self.recv_ACK))
                    #print "ACK sent " + str(self.recv_ACK)
                    if(self.allok and self.allok1):
                        fin_data.append(pkt)
                        count = count+1
			self.ok_packet += 1
                        print "appending the packet is  "+ str(count-1)
		    if(self.sent == 0):
		    	self.send_msg(str(self.ok_packet))
		    	#print "Ok till "+ str(self.ok_packet)
                if(count == no_pkts):
		    #print "waiting for all ok msg."
                    msg6, clientAddress = self.serverSocket.recvfrom(2048)
		    print "last message "+ msg6
                    if (msg6 == "all ok"):
			print "File received completely"
                    	break
            time.sleep(1)
            str1 = ''.join(fin_data)
            with open("snow.jpg","wb") as file2:
                file2.write(base64.decodestring(str1))
                file2.close()
            print "File downloaded"
        

obj2 = client()
obj2.clientRecv()
