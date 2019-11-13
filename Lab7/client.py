from rdt import socket

SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 8080
BUFFER_SIZE = 2048

client = socket()
client.connect((SERVER_ADDR, SERVER_PORT))
while True:
    with open('alice.txt', 'r') as f:
        MESSAGE = f.read()
    client.send(MESSAGE.encode())
    print('Send successfully')
    break
client.close()
