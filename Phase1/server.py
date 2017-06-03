from socket import *
import sys
import time
class server():
    def __init__(self):
        self.serverName = "localhost"
        self.serverPort = 7380
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
    
    def serverSend(self):
        message = raw_input('Input lowercase sentence:')
        print "starting.."
        while 1:
            self.clientSocket.sendto(message,(self.serverName, self.serverPort))
            print "sending"
            time.sleep(1)
            print "message sent"
            print "Ready to recieve"
            modifiedMessage, serverAddress = self.clientSocket.recvfrom(2048)
            print modifiedMessage
            print "sending image"
            file_name = "/Users/arpitsaxena/Desktop/ndc/image.jpg"
            f = open(file_name,'rb')
            data = f.read(9*1024)
            #clientSocket.sendto(data,(serverName, serverPort))
            while (data):
                if(self.clientSocket.sendto(data,(self.serverName, self.serverPort))):
                    print "sending ..."
                    data = f.read(9*1024)
                    break
            break

obj1 = server()
obj1.serverSend()