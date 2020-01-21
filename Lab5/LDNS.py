# encoding:GBK
"""
Created on 2019年10月12日

@author: lct
"""
from socket import *
import time
import struct

DNS_SERVER = ('114.114.114.114', 53)
CACHE = {}
CACHE_TTL = 60


class DNSHeader:  # Code form lab to decode the header
    Struct = struct.Struct('!6H')

    def __init__(self):
        self.__dict__ = {
            field: None
            for field in
            ('ID', 'QR', 'OpCode', 'AA', 'TC', 'RD', 'RA', 'Z', 'RCode', 'QDCount', 'ANCount', 'NSCount', 'ARCount')}

    def parse_header(self, data):
        self.ID, misc, self.QDCount, self.ANCount, self.NSCount, self.ARCount = DNSHeader.Struct.unpack_from(data)
        self.QR = (misc & 0x8000) != 0
        self.OpCode = (misc & 0x7800) >> 11
        self.AA = (misc & 0x0400) != 0
        self.TC = (misc & 0x200) != 0
        self.RD = (misc & 0x100) != 0
        self.RA = (misc & 0x80) != 0
        self.Z = (misc & 0x70) >> 4  # Never used
        self.RCode = misc & 0xF

    def __str__(self):
        return '<DNSHeader {}>'.format(str(self.__dict__))


class Resolver:  # Resolver is used to analyse the query and response message
    def __init__(self, message):
        self.r_data = []
        self.data_length = []
        self.ttl = []
        self.answer_class = []
        self.answer_type = []
        self.answer_name = []
        self.question_name = []
        self.question_class = 0
        self.question_type = 0
        self.index = 12
        self.data = list(message)
        self.id = self.data[0:2]
        self.header = message[0:12]
        self.dh = DNSHeader()
        self.dh.parse_header(self.header)

    def _get_question(self):  # This method can get the question (name,type,class)
        while self.data[self.index] != 0:
            label = ''
            for j in range(self.data[self.index]):
                label += chr(self.data[self.index + j + 1])
            self.question_name.append(label)
            self.index += self.data[self.index] + 1
        self.index += 1
        self.question_type = self.data[self.index] * 256 + self.data[self.index + 1]
        self.index += 2
        self.question_class = self.data[self.index] * 256 + self.data[self.index + 1]
        self.index += 2
        return '.'.join(self.question_name), self.question_type, self.question_class

    def get_question(self):
        if self.question_name:
            return '.'.join(self.question_name), self.question_type, self.question_class
        return self._get_question()

    def get_answer(self):  # This method can get the ttl of each answer
        self.get_question()
        compression = False
        for i in range(self.dh.ANCount + self.dh.NSCount):
            index = self.index
            temp_answer_name = []
            while self.data[index] != 0:
                if self.data[index] >= 192:
                    compression = True
                    index = (self.data[index] - 192) * 256 + self.data[index + 1]
                answer_label = ''
                for j in range(self.data[index]):
                    answer_label += chr(self.data[index + j + 1])
                temp_answer_name.append(answer_label)
                index += self.data[index] + 1
            self.answer_name.append('.'.join(temp_answer_name))
            index += 1
            if not compression:
                self.index = index
            else:
                self.index += 2
            self.answer_type.append(self.data[self.index] * 256 + self.data[self.index + 1])
            self.index += 2
            self.answer_class.append(self.data[self.index] * 256 + self.data[self.index + 1])
            self.index += 2
            ttl = 0
            tp = self.index
            for j in range(4):
                ttl += (ttl * 256 + self.data[self.index + j])
            self.ttl.append((tp, ttl))
            self.index += 4
            self.data_length.append(self.data[self.index] * 256 + self.data[self.index + 1])
            self.index += 2
            rd = 0
            for j in range(self.data_length[i]):
                rd += (rd * 256 + self.data[self.index + j])
            self.r_data.append(rd)
            self.index += self.data_length[i]
        return Answer(self.ttl, self.data)

    def get_response(self, answer):  # This method can change the id of response
        response = answer.response
        response[0:2] = self.id
        return response


class Answer:  # This Answer class with ttl and response are stored in cache as value
    def __init__(self, ttl, response):
        self.ttl = ttl
        self.response = response
        self.time = time.time()


def up_query(query_message):  # Up query to get the response message
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto(query_message, DNS_SERVER)
    return clientSocket.recvfrom(2048)[0]


if __name__ == '__main__':
    start_time = time.time()
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('127.0.0.1', 53))
    print('The server is ready to receive')
    while True:
        break_flag = False
        if int(time.time() - start_time) >= CACHE_TTL:  # Clean out the cache every CACHE_TTL
            start_time = time.time()
            for key, answer in CACHE.items():
                for ttl_index, ttl in answer.ttl:
                    if ttl < int(time.time() - answer.time):
                        print('Clean out cache')
                        CACHE[key] = None
                        break_flag = True
                        break
                if break_flag:  # Each CACHE_TTL clean out one corrupted answer
                    break_flag = False
                    break
        message, client_address = serverSocket.recvfrom(2048)
        question_resolver = Resolver(message)
        question = question_resolver.get_question()
        try:
            answer = CACHE[question]  # KeyError occurs when cache don't have its value
            print('Cache Hit')
            break_flag = False
            for ttl_index, ttl in answer.ttl:
                if ttl <= int(time.time() - answer.time):  # ttl exceeds and up query
                    print('The ttl exceeds, up query and refresh cache')
                    response = up_query(message)
                    answer_resolver = Resolver(response)
                    CACHE[question] = answer_resolver.get_answer()
                    break_flag = True
                    break
            if not break_flag:  # Change the ttl if the answer's ttl don't exceed
                for ttl_index, ttl in answer.ttl:
                    V = 256 * 256 * 256 * 256
                    new_ttl = ttl - int(time.time() - answer.time)
                    for i in range(4):
                        V /= 256
                        answer.response[ttl_index + i] = int(new_ttl // V)
                        new_ttl = new_ttl % V
            response = bytes(question_resolver.get_response(answer))
        except KeyError:
            print('Cache Miss')  # Cache miss and up query
            response = up_query(message)
            answer_resolver = Resolver(response)
            CACHE[question] = answer_resolver.get_answer()
            serverSocket.sendto(response, client_address)
        serverSocket.sendto(response, client_address)
