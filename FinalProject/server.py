import sys
import optparse
import socket
import select
import errno
import pytun
import time

buffer = {i: {} for i in range(1, 256)}
# 全局变量
Waiting_payload = []
Sended_payload = {}


# 构建TXT answer
def create_dns_packet(ID, payload, payload_from_client):
    packet = []
    payload = list(payload)
    payload_len = len(payload)
    flag = [0x81, 0x80]  # [0x81, 0x80]
    num_q = [0x00, 0x01]
    num_ans_rr = [0x00, 0x01]
    num_aut_rr = [0x00, 0x00]
    num_add_rr = [0x00, 0x00]
    Queries = [0x08, 0x67, 0x72, 0x6f, 0x75, 0x70, 0x2d, 0x32, 0x31, 0x05, 0x63, 0x73, 0x33, 0x30, 0x35, 0x03, 0x66,
               0x75, 0x6e, 0x00]  # group-21.cs305.fun
    type = [0x00, 0x10]  # TXT
    clas = [0x00, 0x01]
    packet += ID
    packet += flag
    packet += num_q
    packet += num_ans_rr
    packet += num_aut_rr
    packet += num_add_rr
    if payload_from_client:
        payload_from_client = list(payload_from_client)
        payload_from_client_len = len(payload_from_client)
        name = []
        while payload_from_client_len > 63:
            name += [63]  # 1 bytes
            name += payload_from_client[:63]
            payload_from_client_len -= 63
            payload_from_client = payload_from_client[63:]
        name += [payload_from_client_len]
        name += payload_from_client
        name += Queries
        packet += name
    else:
        packet += Queries
    packet += type
    packet += clas

    name = [0xc0, 0x0c]
    type = [0x00, 0x10]  # TXT
    ttl = [0x00, 0x00, 0x00, 0x00]  # 不能设置ttl
    packet += name
    packet += type
    packet += clas
    packet += ttl
    if payload_len <= 255:
        packet.append((payload_len + 1) // 256)
        packet.append((payload_len + 1) % 256)
        packet.append(payload_len)
        packet += payload
    else:
        packet.append(1)
        packet.append((payload_len + 2) % 256)
        packet.append(255)
        packet += payload[0:255]
        payload_len -= 255
        packet.append(payload_len)
        packet += payload[255:]
    return bytes(packet)


def parse_dns_packet(packet):
    packet = list(packet)
    if packet[12] == 2:  # 前两个bytes为标识simple query
        payload = packet[13:13 + packet[12]]
        return 0, 0, 0, packet[0:2], bytes(payload), True, packet[13] * 256 + packet[14]
    else:
        payload = []
        index = 12
        Bid, Sid, maxS = packet[13], packet[14], packet[15]
        payload += packet[index + 4:index + 1 + packet[index]]
        index += (1 + packet[index])
    while packet[index] == 63:
        payload += packet[index + 1:index + 1 + packet[index]]
        index += (1 + packet[index])
    if packet[index] == 8 and packet[index + 1: index + 1 + 8] == [0x67, 0x72, 0x6f, 0x75, 0x70, 0x2d, 0x32, 0x31]:
        pass
    else:
        payload += packet[index + 1:index + 1 + packet[index]]
    return Bid, Sid, maxS, packet[0:2], bytes(payload), False, -1


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
        print('The server is on {}: {}'.format(self._laddr, self._lport))
        print('Listening message from', self._raddr)
        sendBid = 0
        while True:  # socket.read -> tun.write -> socket.write -> tun.read
            try:
                r, w, x = select.select(r, w, x)
                if self._tun in r:
                    to_sock = self._tun.read(mtu)
                    to_sock = list(to_sock)
                    to_sock_len = len(to_sock)
                    if sendBid == 255:
                        sendBid = 0
                    sendBid += 1
                    MaxIndex = to_sock_len // 410  # 251
                    Maximun = (MaxIndex if to_sock_len % 410 == 0 else MaxIndex + 1)
                    for index in range(MaxIndex):
                        little_pack = [sendBid, index, Maximun]
                        little_pack += to_sock[:410]
                        Waiting_payload.append(bytes(little_pack))
                        to_sock_len -= 410
                        to_sock = to_sock[410:]
                    if to_sock_len != 0:
                        little_pack = [sendBid, MaxIndex, Maximun]
                        little_pack += to_sock[:410]
                        Waiting_payload.append(bytes(little_pack))
                    # print('添加了{}个片段进入to_tun buffer'.format(len(Waiting_payload)))
                    to_sock = ''

                if self._sock in r:
                    to_tun, addr = self._sock.recvfrom(99999)
                    Bid, Sid, maxS, ID, to_tun, simple_query, id = parse_dns_packet(to_tun)
                    try:
                        if Sended_payload[id] and time.time() - Sended_payload[id][1] < 0.5:
                            to_sock = create_dns_packet(ID, Sended_payload[id][0], payload_from_client=to_tun)
                            to_tun = ''
                        else:
                            del Sended_payload[id]  # 超时
                            raise KeyError
                    except KeyError:
                        if simple_query:
                            if not Waiting_payload:
                                Sended_payload[id] = (bytes([0, 0]), time.time())
                                to_sock = create_dns_packet(ID, bytes([0, 0]), payload_from_client=to_tun)
                            else:
                                # print('通过一个simple query发送一个片段')
                                Sended_payload[id] = (Waiting_payload[0], time.time())
                                try:
                                    temp = Waiting_payload.pop(0)
                                    # print(list(temp))
                                    to_sock = create_dns_packet(ID, temp, payload_from_client=to_tun)
                                except ValueError as e:
                                    # print('上面那个是错的')
                                    exit(1)
                            to_tun = ''
                        else:
                            # print('获得一个带ip packet的complex query')
                            buffer[(Bid + 246) % 256] = {}
                            if buffer[Bid] == {}:
                                dic = {i: 0 for i in range(0, maxS + 1)}
                                buffer[Bid] = dic
                            if buffer[Bid][Sid] == 0:
                                buffer[Bid][Sid] = list(to_tun)
                                buffer[Bid][maxS] += 1
                            try:
                                if buffer[Bid][maxS] == maxS:
                                    # print('第', Bid, '个包收完片段了')
                                    temp_to_tun = []
                                    for i in range(0, maxS):
                                        temp_to_tun += buffer[Bid][i]
                                    buffer[Bid] = {}
                                    to_tun = bytes(temp_to_tun)
                                else:
                                    # print('第', Bid, '个包还剩', maxS - buffer[Bid][maxS], '片段要收')
                                    to_tun = ''
                            except KeyError as e:
                                print(e)
                                pass
                            to_sock = create_dns_packet(ID, bytes([0, 0]), payload_from_client=to_tun)
                        pass
                    self._rport = addr[1]
                    # if addr[0] != self._raddr:
                    #     to_tun = ''  # drop packet
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
                if self._tun in w:
                    self._tun.write(to_tun)
                    # print(list(to_tun))
                    to_tun = ''
                if self._sock in w:
                    self._sock.sendto(to_sock, (self._raddr, self._rport))
                    to_sock = ''
            except (select.error, socket.error, pytun.Error) as e:
                if e[0] == errno.EINTR:
                    continue
                print(sys.stderr, str(e))
                break


def main():
    parser = optparse.OptionParser()
    parser.add_option('--tun-addr', dest='taddr',
                      help='set tunnel local address')
    parser.add_option('--tun-dstaddr', dest='tdstaddr',
                      help='set tunnel destination address')
    parser.add_option('--tun-netmask', default='255.255.255.0', dest='tmask',
                      help='set tunnel netmask')
    parser.add_option('--tun-mtu', type='int', default=65535, dest='tmtu',
                      help='set tunnel MTU')
    parser.add_option('--local-addr', default='0.0.0.0', dest='laddr',
                      help='set local address [%default]')
    parser.add_option('--local-port', type='int', default=53, dest='lport',
                      help='set local port [%default]')
    parser.add_option('--remote-addr', dest='raddr',
                      help='set remote address')
    parser.add_option('--remote-port', type='int', default=5555, dest='rport',
                      help='set remote port')
    opt, args = parser.parse_args()
    if not (opt.taddr and opt.tdstaddr and opt.raddr and opt.rport):
        parser.print_help()
        return 1
    try:
        server = TunnelServer(opt.taddr, opt.tdstaddr, opt.tmask, opt.tmtu,
                              opt.laddr, opt.lport, opt.raddr, opt.rport)
    except (pytun.Error, socket.error) as e:
        print(sys.stderr, str(e))
        return 1
    server.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
