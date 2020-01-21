import sys
import optparse
import socket
import select
import errno
import pytun
import random
import time

count1 = 0
count2 = 0
ID1 = 0
ID2 = 0
buffer = {i: {} for i in range(1, 256)}


# 发起TXT询问
def create_dns_packet(payload=None, simple_query=False):
    global ID1
    global ID2
    ID1 += 1
    if ID1 >= 255:
        ID2 += 1
        ID1 %= 255
    ID2 %= 255
    ID = [ID2, ID1]
    packet = []

    flag = [0x01, 0x00]
    num_q = [0x00, 0x01]
    num_ans_rr = [0x00, 0x00]
    num_aut_rr = [0x00, 0x00]
    num_add_rr = [0x00, 0x00]
    Queries = [0x08, 0x67, 0x72, 0x6f, 0x75, 0x70, 0x2d, 0x32, 0x31, 0x05, 0x63, 0x73, 0x33, 0x30, 0x35, 0x03, 0x66,
               0x75, 0x6e, 0x00]  # group-21.cs305.fun
    type = [0x00, 0x10]  # TXT
    clas = [0x00, 0x01]  # IN
    packet += ID
    packet += flag
    packet += num_q
    packet += num_ans_rr
    packet += num_aut_rr
    packet += num_add_rr
    if simple_query:
        global count1
        global count2
        count1 += 1
        if count1 >= 255:
            count2 += 1
            count1 %= 255
        count2 %= 255
        Queries = [0x02, count2, count1] + Queries
        packet += Queries
    else:
        payload_len = len(payload)
        name = []
        while payload_len > 63:
            name += [63]  # 1 bytes
            name += payload[:63]  # 0~62 共63 bytes
            payload_len -= 63
            payload = payload[63:]
        name += [payload_len]
        name += payload
        name += Queries
        packet += name
    packet += type
    packet += clas
    return bytes(packet)


def parse_dns_packet(packet):
    packet = list(packet)
    try:
        index = packet.index(192)  # 0xc0
        temp = packet.copy()
        while temp[index + 1] != 12 or temp[index + 3] != 16 or temp[index + 5] != 1 or temp[
            index + 9] != 0:  # 寻找 0xc0 0x0c 到 0x00 以便找到rlength和rdata
            temp = temp[index + 1:]
            index = temp.index(192)
    except ValueError:
        return 0, 0, 0, packet[0:2], ''
    index = index + 12
    if temp[index] == 2 and temp[index + 1] == 0 and temp[index + 2] == 0:  # 回来的payload只有2个bytes，说明不是正常的响应 simple answer
        return 0, 0, 0, packet[0:2], ''
    rlength = temp[index - 2] * 256 + temp[index - 1]  # 2 bytes
    Bid, Sid, maxS = temp[index + 1], temp[index + 2], temp[index + 3]
    payload = temp[index + 4:index + 1 + temp[index]]  # 一个txt的部分
    if rlength > 256:  # 需要判断是否存在第二个txt
        index = index + 1 + temp[index]
        payload += temp[index + 1: index + 1 + temp[index]]
    return Bid, Sid, maxS, packet[0:2], bytes(payload)


Waiting_payload = []


class TunnelServer(object):

    def __init__(self, taddr, tdstaddr, tmask, tmtu, laddr, lport, raddr, rport):
        self._tun = pytun.TunTapDevice(name='tun0', flags=pytun.IFF_TUN)
        self._tun.addr = taddr
        self._tun.dstaddr = tdstaddr
        self._tun.netmask = tmask
        self._tun.mtu = tmtu
        self._tun.up()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((laddr, lport))
        self._raddr = raddr
        self._rport = rport
        self._laddr = laddr
        self._lport = lport

    def run(self):
        mtu = self._tun.mtu
        r = [self._tun, self._sock]
        w = []
        x = []
        to_tun = ''
        to_sock = ''
        print('The client is on {}:{}'.format(self._laddr, self._lport))
        print('Sending message to {}:{}'.format(self._raddr, self._rport))
        Bid = 0
        timeout = 5
        while True:  # socket.read -> tun.write -> socket.write -> tun.read
            try:
                simple_query = create_dns_packet(simple_query=True)
                self._sock.sendto(simple_query, (self._raddr, self._rport))
                r, w, x = select.select(r, w, x, timeout)
                if self._tun in r:
                    to_sock = self._tun.read(mtu)
                    to_sock = list(to_sock)
                    # print(to_sock)
                    to_sock_len = len(to_sock)
                    # 将大包分成多个小包
                    if Bid == 255:
                        Bid = 0
                    Bid += 1  # 大包id
                    MaxIndex = to_sock_len // 217
                    Maximun = (MaxIndex if to_sock_len % 217 == 0 else MaxIndex + 1)
                    for index in range(MaxIndex):
                        little_pack = [Bid, index, Maximun]
                        little_pack += to_sock[:217]
                        Waiting_payload.append(bytes(little_pack))
                        to_sock_len -= 217
                        to_sock = to_sock[217:]
                    if to_sock_len != 0:
                        little_pack = [Bid, MaxIndex, Maximun]
                        little_pack += to_sock[:217]
                        Waiting_payload.append(bytes(little_pack))
                    to_sock = Waiting_payload.pop(0)
                    # print('添加{}个片段进入to_sock buffer'.format(len(Waiting_payload)+1))
                if self._sock in r:
                    to_tun, addr = self._sock.recvfrom(99999)
                    recvBid, Sid, maxS, ID, to_tun = parse_dns_packet(to_tun)
                    if recvBid != 0:
                        buffer[(Bid + 246) % 256] = {}
                        if buffer[recvBid] == {}:
                            dic = {i: 0 for i in range(0, maxS + 1)}
                            buffer[recvBid] = dic
                        if buffer[recvBid][Sid] == 0:
                            buffer[recvBid][Sid] = list(to_tun)
                            try:
                                buffer[recvBid][maxS] += 1
                            except TypeError:
                                pass
                        try:
                            if buffer[recvBid][maxS] == maxS:
                                # print('第', recvBid, '个包收完片段了')
                                temp_to_tun = []
                                for i in range(0, maxS):
                                    temp_to_tun += buffer[recvBid][i]
                                to_tun = bytes(temp_to_tun)
                                buffer[recvBid] = {}
                                # print(temp_to_tun)
                            else:
                                # print('第', recvBid, '个包还剩', maxS - buffer[recvBid][maxS], '片段要收')
                                to_tun = ''
                        except KeyError as e:
                            print(e)
                            pass
                    # addr[0] != self._raddr or
                    if addr[1] != self._rport:
                        to_tun = ''  # drop packet
                if self._tun in w:
                    self._tun.write(to_tun)
                    to_tun = ''
                if self._sock in w:
                    # print('发送了{}个片段'.format(len(Waiting_payload)+1))
                    to_sock = create_dns_packet(to_sock, simple_query=False)
                    self._sock.sendto(to_sock, (self._raddr, self._rport))
                    while Waiting_payload:
                        to_sock = create_dns_packet(Waiting_payload.pop(0), simple_query=False)
                        self._sock.sendto(to_sock, (self._raddr, self._rport))
                    to_sock = ''

                r = []
                w = []
                if to_tun:
                    w.append(self._tun)
                else:
                    r.append(self._sock)
                if to_sock:
                    w.append(self._sock)
                else:
                    r.append(self._tun)
            except (select.error, socket.error, pytun.Error) as e:
                if e[0] == errno.EINTR:
                    continue
                print(sys.stderr, str(e))
                break


def main():
    parser = optparse.OptionParser()
    parser.add_option('--tun-addr', dest='taddr', help='set tunnel local address')
    parser.add_option('--tun-dstaddr', dest='tdstaddr', help='set tunnel destination address')
    parser.add_option('--tun-netmask', default='255.255.255.0', dest='tmask', help='set tunnel netmask')
    parser.add_option('--tun-mtu', type='int', default=65535, dest='tmtu', help='set tunnel MTU')
    parser.add_option('--local-addr', default='0.0.0.0', dest='laddr', help='set local address [%default]')
    parser.add_option('--local-port', type='int', default=5555, dest='lport', help='set local port [%default]')
    parser.add_option('--remote-addr', dest='raddr', help='set remote address')
    parser.add_option('--remote-port', type='int', default=53, dest='rport', help='set remote port')
    opt, args = parser.parse_args()
    if not (opt.taddr and opt.tdstaddr and opt.raddr and opt.rport):
        parser.print_help()
        return 1
    try:
        server = TunnelServer(opt.taddr, opt.tdstaddr, opt.tmask, opt.tmtu, opt.laddr, opt.lport, opt.raddr, opt.rport)
    except (pytun.Error, socket.error) as e:
        print(sys.stderr, str(e))
        return 1
    server.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
