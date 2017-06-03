from socket import *
import sys

class client():
    def __init__(self):
        self.serverPort = 7380
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind(('',self.serverPort))
        print "The server is ready to receive"
    
    def clientRecv(self):
        while 1:
            print "receiving.."
            message, clientAddress = self.serverSocket.recvfrom(2048)
            print (message)
            modifiedMessage = message.upper()
            self.serverSocket.sendto(modifiedMessage, clientAddress)
            print "lets receive the image"
            file_name = "/Users/arpitsaxena/Desktop/ndc/image2.jpg"
            f = open(file_name,'wb')
            data,addr = self.serverSocket.recvfrom(9*1024)
            try:
                while(data):
                    f.write(data)
                    self.serverSocket.settimeout(2)
                    data,addr = self.serverSocket.recvfrom(9*1024)
            except timeout:
                    print "File Downloaded"
                    break


obj = client()
obj.clientRecv()
    