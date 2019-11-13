from rdt import socket

SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 8080
BUFFER_SIZE = 2048

server = socket()
server.bind((SERVER_ADDR, SERVER_PORT))

print('Server start at', SERVER_ADDR)
with open('alice.txt', 'r') as f:
    MESSAGE = f.read()
while True:
    data = server.recv()
    data = data.decode()
    print(data == MESSAGE)
    break
