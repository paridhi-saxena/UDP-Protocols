import base64
import sys
import time
from socket import *

class server():
    def __init__(self):
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverName = "localhost"
        self.serverPort = 7380
        self.pkt_size = 1024
        self.c_size = str(self.pkt_size)
    
    def send_msg(self, msg):
        self.clientSocket.sendto(msg,(self.serverName, self.serverPort))
        time.sleep(1)
    
    def make_packets(self,data):
        file_size = len(data)
        no_pkts = file_size/self.pkt_size
        rem1 = file_size % self.pkt_size
        if(rem1):
            no_pkts = no_pkts+1
        print no_pkts
        c_pkts = str(no_pkts)
        pkt = []
        for i in range (0,no_pkts):
            pkt.append(data[i*self.pkt_size:(i+1)*self.pkt_size])
            print i
            print "******************"
            #print pkt
        print "starting.."
        self.send_msg("no of packets")
        print "sending file size"
        self.send_msg(c_pkts)
        self.send_msg("packet size")
        self.send_msg(self.c_size)
        return pkt
    
    def serverSend(self):
        with open("image.jpg","rb") as file1:
        	str1 = base64.b64encode(file1.read())
        	pkts = self.make_packets(str1)
        	while 1:
            		print "Sending pkts now.."
            		for x in pkts:
                		self.send_msg(x)
                		print "Sent packet"
            		file1.close()
            		break

obj1 = server()
obj1.serverSend()









