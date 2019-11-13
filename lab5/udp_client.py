#encoding:GBK
#!/usr/bin/env python3
'''
Created on 2019��10��12��

@author: lct
'''

from socket import *
serverName = '127.0.0.1'
serverPort = 12000
clientSocket = socket(AF_INET,SOCK_DGRAM)
message = input('please input the ')
clientSocket.send(message)