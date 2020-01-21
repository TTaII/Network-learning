# Chapter 6: Link layer and LANs
## 6.1 Introduction
+ layer-2 packet: frame, encapsulates datagram
+ links
  + wired links
  + wireless links
+ half-duplex and full-duplex: 单方向和双方向
+ link layer implemented in "adaptor" aka network interface and NIC or on a chip(适配器)
  + Ethernet card, 802.11 card; Ethernet chipset
  + implemnets link, physical layers
## 6.2 Error detection, correction
+ EDC=Error Detection and Correction bits(redundancy)
+ Actually ED is not 100% reliable
  + may miss some errors but rarely
+ Parity checking
  + single bit parity: detect single bit errors
  + two-dimensional bit parity: detect and correct single bit errors.
+ Cyclic redundancy check(widely used in practice Ethernet, 802.11 WiFi, ATM)
  + more powerful error-detection coding
  + data bits: D
  + choose r+1 bit pattern(generator): G
  + choose r CRC bits: R such that 发送端发送<D，R>接收端除G，如果余数不为零说明有errors
  + can detect all burst errors less than r+1 bits 
  + 过程(乘2^r是为了左移r bits，xor R是为了在后面的bit加上R)
    + 在发送端通过计算$R=remainder(\frac{D*2^r}{G})$获得r bits长的R
    + 接收端检验R:计算$remainder(\frac{<D,R>}{G}$是否为0
## 6.3 Multiple access protocols(多路访问协议)
+ Two types of 'links':
  + point-to-point
    + PPP for dial-up access
  + broadcast(shared wire or medium)
    + old-fashioned Ethernet
    + 802.11 wireless LAN
+ collision if onde node receives two or more signals at the same time
+ Channel partitioning protocol
  + TDMA(time division multiple access)
  + FDMA(frequency division multiple access)
  + CDMA(code division multiple access 码分多址)
    + 为不同结点分配不同的编码使得不同结点能同时传输，并且各自相应的接收方能正确接收发送方编码的数据比特(假设接收方知道发送方的编码)
  + Unused resource go idle
+ Random access protocols
  + 一个传输结点总是以信道的全部速率(R bps)进行发送。涉及碰撞的每个结点反复重发帧直到无碰撞为止。但是结点不是立即重发，而是等待一个随机时延。
  + no coordinantion
  + how to detect collisions
  + how to recover from collisions
  + examples of random access MAC protocols
    + slotted ALOHA
    + ALOHA
    + CSMA, CSMA/CD, CSMA/CA
+ Slotted ALOHA(时隙ALOHA)
  + 所有帧大小为L bits
  + 所有结点同步，每个结点都知道时隙的开始时间
  + 一个slot长度为L/R 即表示一个slot为以全速R传输一帧的时间
  + each slot is equal to one frame
  + 结点会在碰撞的那个slot结束前检测到碰撞，并以概率p考虑是否立即重发这一帧。以1-p的概率表示下一个slot再考虑概率p
  + $N*p*(1-p)^{N-1}$ = 0.37说明当N趋近无穷时，最多有37%的slot是成功slot，即100Mbps的实际成功吞吐量将小于37Mbps
+ Pure (unsloted) ALOHA
  + 结点不同步？网络层下发数据包时立即传输这一帧
  + 关注某个单独的结点来计算效率
  + 在一个结点的起始和结束部分不能有重叠[t0-1,t0],[t0,t0+1]>>$(1-p)^{2(N-1)}$
  + 传输成功>>$N*p*(1-p)^{2(N-1)}$>>最大效率=18%
+ CSMA(carrier sense(载波侦听) multiple access)
  + 说话之前先听(send if channel sensed idle else defer)
  + 如果与他人同时开始说话，停止说话(碰撞检测)，等待随机一段时间，重复(侦听-当空闲时传输)循环
+ CSMA/CD(collision detection)
  + 碰撞检测原理，适配器(NIC)
    + 适配器从网络层获得数据报，封装成链路层帧，并放入帧适配器缓存中
    + 适配器负责侦听信道和传输帧，直到信道上没有信号能量时开始传输帧
    + 传输过程中，侦听其他适配器的信号能量
    + 若整个传输过程，没检测到其他适配器信号能量，表明该帧传输成功，否则中止传输
    + 中止传输后，适配器等待一个随机时间量，然后返回侦听步骤
  + 随机时间量-二进制指数后退算法 等待时间为$K*512$bits
    + 第一次碰撞后从｛0,1｝中等概率选择K
    + 第二次碰撞后从｛0,1,2,3｝中等概率选择K
    + 第n次碰撞后从｛0,1,...,$2^n-1$｝中等概率选择K
  + 效率
    + $\frac{1}{1+\frac{5d_{prop}}{d_{trans}}}$
+ Taking turns(look for best of both worlds)
  + polling protocol(轮询协议)
    + 主结点(master)按顺序给每个结点发送报文，告诉它(结点1)可传输帧的最多数量
    + Pros
      + 不存在碰撞和空slot
    + Cons
      + 轮询时延
      + 减少R传输速率
      + 主结点故障
      + (存在接收到发送报文而没有报文需要发的结点，怎么办)
  + token-passing protocol(令牌传递协议)
    + 一个结点发完最大数量帧后将令牌转给下一个结点
    + 若下一个结点不需要传输帧，则立即转给下一个结点
    + Cons
      + 令牌的开销
      + 单结点故障
### Case study
+ Cable access network
  + DOCSIS(data over cable service interface spec)
  + ?
## 6.4 LANs
### addressing, ARP
+ MAC addresses
  + 48-bit MAC(LAN, physical) address(for most LANs) 在适配器(NIC)上
  + 每个帧实际上会被传输到该LAN下每一个适配器上，适配器会根据目的地址是否为自己的MAC地址来选择是否丢弃他
  + 真正的广播地址(FF-FF-FF-FF-FF-FF)
+ ARP(Address Resolution Protocol, 地址解析协议)
  + ip地址作为输入，获得MAC地址作为输出，来获取子网内想要IP地址的MAC地址
  + 限制：只能为在同一个子网内的主机和路由器接口解析IP地址
  + 每个主机或者路由器都具有一个ARP table，包含了IP地址到MAC地址的映射关系还有一个TTL
  + 查询分组和响应分组(格式都相同)
    + 查询分组的MAC目的地址是广播地址(FF-FF-FF-FF-FF-FF)，IP目的地址为想查询的地址
    + 与之匹配的主机会发送响应ARP分组给源查询主机
  + 属于跨链路层和网络层的协议(因为既包含了MAC地址也包含IP地址)
+ Addressing: Routing to another LAN
  + 111.111.111.111 到 222.222.222.222
  + 帧的MAC目的地址为路由器网关的MAC地址，可以使这一帧上传到路由器的网络层
  + 路由器在网络层处理ip地址的路由，因为路由器保存着222.222.222.xxx的ARP表，可以将该帧的MAC目的地址转为222.222.222.222的MAC地址，使得这个帧到达222.222.222.222的网络层以及以上
### Ethernet
+ 目前：switch Ethernet(交换机是无碰撞且存储转发分组)
+ 以太网帧的结构(从尾部到头部)
  + CRC(4)  
  + 数据字段(46~1500)
  + 类型(2)
  + 目的地址(6) 目的适配器的MAC地址
  + 源地址(6) 
  + preamble(前同步码)(8): 告诉接受者包的开始，校准接收端的clock 7bytes with 10101010 1byte with 10101011
+ unreliable, connectionless
  + no handshaking
  + physically reliable, so there are no ack and nak
  + 因为TCP重传可以保证reliable，实际上只是以太网适配器不知道接受或者发送的数据是新的还是重传的数据报
  + Ethernet's MAC protocol: unslotted CSMA/CD with binary backoff
### Switch
+ filtering and forwarding
+ switch table
  + 地址-接口-时间(star结构，一个接口意味着一台主机或者另一个switch)
+ 数据转发(目的地址DD-DD-DD-DD-DD-DD)
  + 表中没有这条表项, 交换机广播该帧
  + 若目的接口为来的接口，过滤(说明帧从包含该目的地址的局域网来)
  + 若目的接口不为来的接口，放到该接口的输出缓存即完成了转发功能
+ link-layer device: takes an active role
+ transparent
+ plug-and-play, self-learning
  + do not need to be configured
+ Properties
  + Elimination of collisions
  + Heterogeneous links(异质的链路，将链路彼此隔离)
  + Management
### VLANs
+ Motivation
  + 流量隔离
  + 管理用户
+ 基于端口的VLAN(完全隔离)
  + 交换机的端口(接口)由网络管理员划分为组，每个组构成一个vlan，在每个vlan种的端口形成一个广播域
  + 增加干线连接来接入别的用户
+ 基于MAC的VLAN
  + 指定属于某个VLAN的MAC地址
+ 也能基于网络层协议设置VLAN(ipv4, ipv6)
### Data center network
+ 略
### A day in the life of a web request
+ DHCP(UDP, IP), broadcast on LAN
+ DNS(UDP)
  + ARP find the MAC of first-hop router
  + RIP or BGP to DNS sever
+ HTTP(TCP)