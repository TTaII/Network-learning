#encoding:GBK
'''
Created on 2019��10��12��

@author: lct
'''
from socket import *
import time
import struct

UPDNS = '114.114.114.114'
PORT = 53  
CACHE = {}
CACHE_TTL = 60

class DNSHeader:# Code form lab to decode the header
    Struct = struct.Struct('!6H')
    def __init__(self):
        self.__dict__ = {
            field: None
            for field in ('ID', 'QR', 'OpCode', 'AA', 'TC', 'RD', 'RA', 'Z','RCode', 'QDCount', 'ANCount', 'NSCount', 'ARCount')}
    def parse_header(self, data):
        self.ID, misc, self.QDCount, self.ANCount, self.NSCount, self.ARCount = DNSHeader.Struct.unpack_from(data)
        self.QR = (misc & 0x8000) != 0
        self.OpCode = (misc & 0x7800) >> 11
        self.AA = (misc & 0x0400) != 0
        self.TC = (misc & 0x200) != 0
        self.RD = (misc & 0x100) != 0
        self.RA = (misc & 0x80) != 0
        self.Z = (misc & 0x70) >> 4 # Never used
        self.RCode = misc & 0xF
    def __str__(self):
        return '<DNSHeader {}>'.format(str(self.__dict__))
class Resolver():# Resolver is used to analyse the query and response message
    def __init__(self, message):
        self.data = list(message)
        self.id = self.data[0:2]
        self.header = message[0:12]
        self.dh = DNSHeader()
        self.dh.parse_header(self.header)
    def get_question(self):# This method can get the question (name,type,class)
        self.qname = []
        self.index = 12
        while self.data[self.index]!=0:
            str=''
            for j in range(self.data[self.index]):
                str+=chr(self.data[self.index+j+1])
            self.qname.append(str)
            self.index+=self.data[self.index]+1
        self.index+=1
        self.qtype = self.data[self.index]*256+self.data[self.index+1]
        self.index+=2
        self.qclass = self.data[self.index]*256+self.data[self.index+1]
        self.index+=2
        return ('.'.join(self.qname),self.qtype,self.qclass)
    def get_answer(self):# This method can get the ttl of each answer
        self.get_question()
        yasuo = False
        self.name = []
        self.type = []
        self.clas = []
        self.ttl = []
        self.dlen = []
        self.rdate = []
        for i in range(self.dh.ANCount+self.dh.NSCount):
            index = self.index
            strl=[]
            while self.data[index]!=0:
                if self.data[index]>=192:
                    yasuo = True
                    index = (self.data[index]-192)*256+self.data[index+1]
                str = ''
                for j in range(self.data[index]):
                    str+=chr(self.data[index+j+1])
                strl.append(str)
                index+=self.data[index]+1
            self.name.append('.'.join(strl))
            index+=1
            if not yasuo:
                self.index = index
            else:
                self.index+=2
            self.type.append(self.data[self.index]*256+self.data[self.index+1])
            self.index+=2
            self.clas.append(self.data[self.index]*256+self.data[self.index+1])
            self.index+=2
            ttl = 0
            tp = self.index
            for j in range(4):
                ttl+=(ttl*256+self.data[self.index+j])
            self.ttl.append((tp,ttl))
            self.index+=4
            self.dlen.append(self.data[self.index]*256+self.data[self.index+1])
            self.index+=2
            rd = 0
            for j in range(self.dlen[i]):
                rd+=(rd*256+self.data[self.index+j])
            self.rdate.append(rd)
            self.index+=self.dlen[i]
        return Answer(self.ttl,self.data)
    def get_response(self,answer):# This method can change the id of response
        response = answer.response
        response[0:2] = self.id
        return response
    
class Answer():# This Answer class with ttl and response are stored in cache as value
    def __init__(self,ttl,response):
        self.ttl = ttl
        self.response = response
        self.time = time.time()
    
        
def UPStream(message):# Upquery to get the response message
    clientSocket = socket(AF_INET,SOCK_DGRAM)
    clientSocket.sendto(message,(UPDNS,PORT))
    response,UPDNSadd = clientSocket.recvfrom(2048)
    return response
    


if __name__ == '__main__':
    starttime = time.time()
    serverPort = 53
    serverSocket = socket(AF_INET,SOCK_DGRAM)
    serverSocket.bind(('127.0.0.1',serverPort))
    print('The server is ready to receive')
    while True:  
        break_flag = False
        if int(time.time()-starttime)>=CACHE_TTL:# Clean out the cache every CACHE_TTL
            starttime = time.time()
            for key,answer in CACHE.items():
                tlen = int(time.time()-answer.time)
                for tp,ttl in answer.ttl:
                    if ttl<tlen:
                        print('Clean out cache')
                        del CACHE[key]
                        break_flag = True
                        break
                if break_flag:# Each CACHE_TTL clean out one corrupted answer
                    break_flag=False
                    break
        message,clientAddress = serverSocket.recvfrom(2048)
        Qresolver = Resolver(message)
        question = Qresolver.get_question()
        break_flag = False
        try:
            answer = CACHE[question]# KeyError occurs when cache don't have its value
            print('Cache Hit')
            tlen = int(time.time()-answer.time)
            for tp,ttl in answer.ttl:
                if ttl <= tlen:#ttl exceeds and upquery
                    print('The ttl exceeds,upquery and refresh cache')
                    response = UPStream(message)
                    Aresolver = Resolver(response)
                    CACHE[question] = Aresolver.get_answer()
                    break_flag = True
                    break
            response = Qresolver.get_response(answer)
            if not break_flag:#Change the ttl if the answer's ttl don't exceed
                for tp,ttl in answer.ttl:
                    V = 256*256*256*256
                    t = ttl - tlen
                    for i in range(4):
                        V/=256
                        answer.response[tp+i] = int(t//V)
                        t = t % V
            response = bytes(response)                 
        except KeyError:
            print('Cache Miss')#Cache miss and upquery
            response = UPStream(message)
            Aresolver = Resolver(response)
            CACHE[question]=Aresolver.get_answer()
            serverSocket.sendto(response,clientAddress)
        serverSocket.sendto(response,clientAddress)
        