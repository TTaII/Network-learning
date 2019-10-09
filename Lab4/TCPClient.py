#encoding:GBK
'''
Created on 2019年10月3日

@author: lct
'''
from socket import *
client_server = socket(AF_INET,SOCK_STREAM)
client_server.connect(('127.0.0.1',5555))
while True:
    message = input("Input something:")
    client_server.send(message.encode())
    motifiedmessage = client_server.recv(1024)
    print(motifiedmessage.decode())
client_server.close()