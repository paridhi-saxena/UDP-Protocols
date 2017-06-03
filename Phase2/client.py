from socket import *
import sys
import base64

class client():
    def __init__(self):
        self.serverPort = 7380
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind(('', self.serverPort))
        print "Server is ready to recieve!"
    
    def clientRecv(self):
        while 1:
            msg1, clientAddress = self.serverSocket.recvfrom(2048)
            print msg1
            if (msg1 == "no of packets"):
                    no_pkts, clientAddress = self.serverSocket.recvfrom(2048)
                    print no_pkts
            msg2, clientAddress = self.serverSocket.recvfrom(2048)
            print msg2
            if (msg2 == "packet size"):
                pkt_size, clientAddress = self.serverSocket.recvfrom(2048)
                print pkt_size
            no_pkts = int(no_pkts)
            pkt_size = int(pkt_size)
            count = 0
            fin_data =[]
            while 1:
                pkt, addr = self.serverSocket.recvfrom(pkt_size)
                if(pkt):
                    count = count+1
                    fin_data.append(pkt)
                    if(count == no_pkts):
                        break
            str = ''.join(fin_data)
            with open("new_image.jpg","wb") as file2:
                file2.write(base64.decodestring(str))
                file2.close()
            print "File downloaded"
            break

			 		
obj2 = client()
obj2.clientRecv()
