from udp import UDPsocket  # import provided class

SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 8080


class payload:
    def __init__(self, MTU):
        self.SYN = 0
        self.FIN = 0
        self.ACK = 0
        self.SEQ = 0
        self.ACKNum = 0
        self.LEN = 0
        self.parse_Len = 0
        self.payload = None
        self.check = False

    def calc_checksum(self, message):
        sum = 0
        T = 0
        temp = 0
        for i in range(len(message)):
            if i == 13 or i == 14 or i == 0:
                continue
            byte = message[i]
            # print(byte)
            T += 1
            if T == 1:
                temp += byte
            if T == 2:
                temp = temp * 256 + byte
                sum += temp
                sum = sum & 0xFFFF
                T = 0
        checksum = message[13] * 256 + message[14]
        sum -= checksum
        return sum

    def parse_Payload(self, message):
        Flag = message[0]
        self.SYN = (0 if Flag & 0x4 == 0 else 1)
        self.FIN = (0 if Flag & 0x2 == 0 else 1)
        self.ACK = (0 if Flag & 0x1 == 0 else 1)
        self.SEQ = 0
        for i in range(1, 5):
            self.SEQ = message[i] + self.SEQ * 256
        self.ACKNum = 0
        for i in range(5, 9):
            self.ACKNum = message[i] + self.ACKNum * 256
        self.parse_Len = 0
        for i in range(9, 13):
            self.parse_Len = message[i] + self.parse_Len * 256
        if self.parse_Len != 0:
            self.payload = message[15:15 + self.parse_Len]
        print('Receive SEQ: {} and ACKNum: {} and LEN: {}'.format(self.SEQ, self.ACKNum, self.parse_Len))
        self.check = self.calc_checksum(message) == 0x0000
        return

    def set_Payload(self, SYN=0, FIN=0, ACK=0, SEQ=0, ACKNum=0, Payload=None) -> bytes:
        print('Set  SEQ: {} and ACKNum: {}'.format(SEQ, ACKNum))
        LEN = (0 if not Payload else len(Payload))
        message = [0 for _ in range(15 + LEN)]
        if LEN != 0:
            message[15:] = Payload
        Flag = SYN * 4 + FIN * 2 + ACK * 1
        message[0] = Flag

        N = 256 * 256 * 256 * 256
        for i in range(1, 5):
            N /= 256
            message[i] = int(SEQ // N)
            SEQ = SEQ % N

        N = 256 * 256 * 256 * 256
        for i in range(5, 9):
            N /= 256
            message[i] = int(ACKNum // N)
            ACKNum = ACKNum % N

        N = 256 * 256 * 256 * 256
        for i in range(9, 13):
            N /= 256
            message[i] = int(LEN // N)
            LEN = LEN % N
        message[13:15] = [0, 0]

        N = 256 * 256
        checksum = self.calc_checksum(message)
        for i in range(13, 15):
            N /= 256
            message[i] = int(checksum // N)
            checksum = checksum % N

        return message


class socket(UDPsocket):
    def __init__(self, Wnd=4, MTU=1500):
        super(socket, self).__init__()
        self.MTU = MTU
        self.Wnd = Wnd
        self.timer = 0
        self.pl = payload(MTU)

    def recv(self, BUFFER_SIZE=2048):  # receiver side
        m = []
        ExpectedSeq = 1
        pl = payload(0)
        ack = pl.set_Payload(ACKNum=ExpectedSeq)
        while True:
            message, ADD = self.recvfrom(BUFFER_SIZE)
            self.ADD = ADD
            pl.parse_Payload(list(message))
            if pl.check and pl.SEQ == ExpectedSeq:
                for byte in pl.payload:
                    m.append(byte)
                ack = pl.set_Payload(ACKNum=ExpectedSeq + pl.parse_Len)
                ExpectedSeq = ExpectedSeq + pl.parse_Len
            self.sendto(bytes(ack), self.ADD)
            if pl.FIN:  # 通知接收端得知此为最后的包，断开连接
                ack = pl.set_Payload(ACK=1, FIN=1)
                self.sendto(bytes(ack), self.ADD)
                print('Get the final packet!')
                break
        return bytes(m)

    def send(self, data):  # sender side
        pl = payload(self.MTU)
        Mess = [0] + list(data)
        length = len(Mess) - 1
        SeqNum = 1
        NextSeqNum = 1
        Win = []
        WinSeq = []
        WinLen = []
        while SeqNum <= length:
            while NextSeqNum < SeqNum + self.Wnd * self.MTU:
                if NextSeqNum > length:
                    break
                if NextSeqNum + self.MTU >= length:
                    pk = pl.set_Payload(FIN=1, SEQ=NextSeqNum, Payload=Mess[NextSeqNum:])
                    WinLen.append(length - NextSeqNum + 1)
                else:
                    pk = pl.set_Payload(SEQ=NextSeqNum, Payload=Mess[NextSeqNum:NextSeqNum + self.MTU])
                    WinLen.append(self.MTU)
                Win.append(pk)
                WinSeq.append(NextSeqNum)
                NextSeqNum += self.MTU
            for pk in Win:
                self.sendto(bytes(pk), self.ADD)
            while True:
                try:
                    self.settimeout(1)
                    data, ADD = self.recvfrom(2048)
                    pl.parse_Payload(data)
                    while True:
                        if WinSeq and WinSeq[0] + WinLen[0] <= pl.ACKNum <= WinSeq[0] + WinLen[0] * len(Win):
                            WinLen.pop(0)
                            Win.pop(0)
                            WinSeq.pop(0)
                            SeqNum += self.MTU
                        else:
                            break
                    if SeqNum == NextSeqNum:
                        break
                except Exception as e:
                    print(e)
                    break
        return
