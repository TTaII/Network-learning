from socket import *
import random, time


class UDPsocket(socket):
    def __init__(self, loss_rate=0.1, corruption_rate=0.1, delay_rate=0.1, delay=0.5):
        super().__init__(AF_INET, SOCK_DGRAM)
        self.timeOut = 1.3
        self.loss_rate = loss_rate
        self.corruption_rate = corruption_rate
        self.delay_rate = delay_rate
        self.delay = delay

    def recvfrom(self, bufsize):
        data, addr = super().recvfrom(bufsize)
        if random.random() < self.loss_rate:
            return self.recvfrom(bufsize)
        if random.random() < self.corruption_rate:
            return self._corrupt(data), addr
        if random.random() < self.delay_rate:
            time.sleep(self.delay)
        return data, addr

    def _corrupt(self, data: bytes) -> bytes:
        raw = list(data)
        for i in range(0, random.randint(0, 3)):
            pos = random.randint(0, len(raw) - 1)
            raw[pos] = random.randint(0, 255)
        return bytes(raw)

    def connect(self, ADD):
        self.ADD = ADD
