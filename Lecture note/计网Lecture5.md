# Lecture 5
## Network layer control plane
+ Chapter goals: understand principles behind network control plane
### introduction
+ data plane: forwarding
+ control plane: routing
+ Two approaches to structuring network control plane
  + pre-router control(traditional)
  + logically centralized control(software defined networking)
    + A remote controller interacts with local control agents (CAs) in routers to compute forwarding tables
### rounting protocol
+ throughput - actual congestion situation on link
+ rate - ideal rate
+ cost - can be congestion situation
+ avaliable rate = rate - cost or cost
+ Two algorithm
  + link state - Dijkstra
    + 若cost不变，dij表现很好
    + 但是cost会根据congestion situation改变
  + distance vector - dynamic programing8
    + 只知道自己到邻居和邻居到目的地的cost和DV 动态规划
    + 维持Dx = [Dx(y):y属于N]
    + cost发生变化，且最低费发生变化, 把自己的DV发给邻居
    + 接收到邻居发的DV就更新自己的DV，用BF等式
    + disadvantage:
### 5.3 Intra AS Routing in the Internet: OSPF
+ autonomous system-AS(自治系统)
+ 在相同的AS中的路由器全部都运行同样的路由选择算法
  + 这种路由选择算法就叫做**自治系统内部路由选择协议(intra-autonomous system routing protocol)**
+ 两个AS间必须运行相同的**自治系统间路由选择协议(inter-autonomous system routing protocol)**
+ internal router and gateway router
+ Forwarding table 实际上是configured by both intra- and inter-AS routing algorithm
+ Intra-AS Routing(interior gateway protocol(IGP)):
  + routing in same AS
  + all routers in AS must run same intra-domain protocol
  + routers in different AS can run different intra-domain routing protocol
  + most common intra-AS routing protocol:
    + RIP(dv-based), OSPF(ls-based),IS-IS, IGRP
+ OSPF
  + Pros
    + 安全，多条相同费用的路径，对单播与多播路有选择的综合支持
### Routing among the ISPs BGP
+ Inter-AS routing
  + routing among AS'es
  + gateways perform inter domain routing (as well as intra domain routing)
+ Inter-AS routing in the Internet: BGP(Border Gateway Protocol)
  + BGP使得每个AS知道经过其相邻AS可达哪些目的地
  + 在各个gateway之间
  + policy may dominate over performance
  + eBGP and iBGP
    + obtain subnet reachability information from neigh AS(eBGP)(AS间外部广播)
    + propagate reachability information to all AS-internal routers(iBGP)(AS内部广播)
  + BGP is a path vector protocol(实际上是广播过程)
  + Path attributes and BGP routes
    + Prefix(destination)+attributes = "route"
    + Two important attributes:
      + AS-PATH
      + NEXT-HOP
    + Policy-based routing:
  + BGP route selection:
    + shortest AS-PATH(AS间距离最短的hop，单位为1)
    + closest NEXT-HOP router: Hot Potato Routing(内部最快的hop，单位为cost)
    + trade-off
+ aggregate routers into regions known as (autonomous system a.k.a 'domains')
  + Gateway router: has links to router in other AS
  + interior router: no link to other AS
## SDN:
+ Why a logically centralized control plane?
  + easier network management
+ 使绑定特定功能的router分层或者规则化使得performance更好
+ 使硬件控制转为软件控制，用os控制。
+ OpenFlow protocol
  + operates between controller and switch
  + Based on TCP
  + Three classes
    + controller-to-switch
    + asynchronous(switch)
    + symmmetric(misc)
## ICMP(internet control message protocol)
+ error reporting: unreachable host, network, port
+ echo request/reply
+ above IP: ICMP msgs carried in IP datagarms
+ format: type, code plus first 8 bytes of IP datagram causing error
+ tracert过程
  + 发送一系列TTL = i, i=0,1,2,3,...,n的request(8,0)
  + 途中接收TTL expired(11,0)
  + 终点接收port unreachable(3,3)
## network management
+ SNMP protocol
