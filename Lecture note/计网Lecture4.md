# Network layer
## Overview
+ implemented in every host and router
+ Two key network-layer function
  + forwarding: process of getting througth single interchange
  + routing: process of planning trip from source to destination
+ Data plane
  + during forwarding
+ Control plane
  + two control-plane approaches
    + Pre-router control plane
        + every router create the forwarding table by themselves
    + Logically centralized control plane
      + software-defined networking
      + since the router is only hardware earlier
      + remote controller calculate the table
+ Network service model
  + multiplexing and demultiplexing
  + no guarantee on bandwidth, loss(rdt), order or timing
  + best effort service
## Router structure
  + each interface has input and output
  + input port function
    + physical layer
    + data link layer
    + decentralized switching(lookup(header field values), forwarding and queue)
  + Longest prefix matching
    + ip地址的继承性
  + Switching fabrics(交换网络)
    + switching rate: rate at which packets can be transfer from input to output
    + three types of switching fabrics
      + memory, bus, crossbar
    + transfer packet from input buffer to appropriate output buffer
  + Output port function
    + buffering
      + RFC 3439 defines the size of buffer
    + scheduling
      + dicard policy
        + tail, random, priority(gets best performance)
  + scheduling policy: priority
    + marked by ip address else.
  + scheduling policy: still more
    + Round Robin(RR): one by one
    + Weighted Fair Queuing(WFQ): Weighted by one
## IP: Internet Protocol
+ overhead: 20 bytes(TCP) + 20 bytes(IP) + applayer overhead
+ IP fragmentation(分片), resassembly(复原)
  + network links have MTU(max.transfer size)
    + different link types will lead to different MTU
    + low transmission rate and high loss rate(WIFI) will lead to small packets
    + packet was cut to different segment but with same ID in header. Each Header(IP header) has length, ID, fragflag, offset and more
    +  length = 1500 -> payload = 1480 -> offset = 1480/8 = 185 since there are not more bits(15bits?) to represent offset
+ IP addressing: introduction
  + network interface card
  + 每个主机或者router有多少个网卡就有多少个ip地址
  + switch can divide many hosts into different subnets
+ IP addressing: CIDR
  + CIDR: Classless InterDomain Routing
  + 20 years ago
    + ClassA: 8bits for mark, 24 bits for subnet's hosts
    + ClassB: 16bits for subnet's hosts
    + ClassC: 8bits for subnet's hosts
+ IP addressing: how to get one?
  + DHCP: Dynamic Host Configuration potocol
    + plug-and-play
    + DHCP discover(using broadcast)
    + DHCP offer
    + DHCP request(using broadcast)
    + DHCP ACK
    + Content in DHCP message(application potocol, using UDP): 
      + address of first-hop router for client(默认网关)
      + name and IP address of DNS sever
      + network mask(indicating network versus host portion of address)
  + hard-coded: 手动设置
+ Internel network address and global network address
  + by using same global network addresses but different ports
  + NAT: network address translation
    + there is a NAT table checked 
    + WAN side addr and LAN side addr
    + motivation:
      + one ip address for many devices
      + change ip address in locao network without notifying outside world
      + change ISP without changing addresses of devices in local network
      + devices inside local net not explicitly addressable, visible by outside world
    + it is controversial:
      + router should only process up to layer 3
      + violate end-to-end argument(e.g., P2P is useless when you change the ip internel address)
+ IPv6
  + motivation: to provide more addresses -> $2^{128}$
  + additional motivation:
    + header format helps speed processing/forwarding
    + header changes to facilitate QoS
  + IPv6 datagram format(PPT 27):
    + fixed-length 40 bytes header
    + no fragmentation allowed(Important)
  + Other Changes from IPv4
    + No checksum
    + options: allowed but outside of header
    + ICMPv6
  + 后向兼容:使ipv6兼容ipv4，ipv6可以完成ipv4的所有服务(EDNS)
  + problem：
    + ipv4 router 无法理解 ipv6的包
    + ipv6 router 可以理解 ipv4的包
    + ipv6 router 把包封装成ipv4的包
## Generalized Forwarding and SDN - software define networking
  + A remote(centre) controller
  + flow: defined by header fields(where?)
  + flow table (根据header match，然后做相应action)
  + protocol——openflow
    + flow-defined by headers
    + Rules - headers(from link layer(switch) to Transport layer)
    + Action(drop, forward, modify, matched packet or send matched packet to controller)
    + Status- packet and byte -> counter
  + match+action:统一不同的设备，比如router, Switch(dst:MAC addr, FireWall, NAT(modify))
  + Example：
    + ![](截图/TIM图片20191118105112.png)