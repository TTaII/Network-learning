#encoding:GBK
'''
Created on 2019��9��30��

@author: lct
'''
from socket import *
message = b'-D\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x03www\x05baidu\x03com\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x0c\x00\n\x00\x08p\xfd\xa1\xbfk\x11!\xec'
d = [45, 68, 1, 32, 0, 1, 0, 0, 0, 0, 0, 1, 3, 119, 119, 119, 5, 98, 97, 105, 100, 117, 3, 99, 111, 109, 0, 0, 1, 0, 1, 0, 0, 41, 16, 0, 0, 0, 0, 0, 0, 12, 0, 10, 0, 8, 112, 253, 161, 191, 107, 17, 33, 236]
data = list(message)
print(data)
print(message)
print(bytes(d))
# for i in range(d.__len__()):
#     print(hex(d[i]),end=' ')
c = {1:'123',3:'123321'}
for key,value in c.items():
    print(key,value)
v = 256
v/=2
print(v//3)
