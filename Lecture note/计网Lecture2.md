# **Chapter 2**
## **2.1 Principles of network applications**
### application architecture
+ client-server architecture
+ P2P architecture
  + self-scalability(自扩展性)
  + 未来三大主要挑战
    + ISP友好（非对称的带宽）
    + 安全性（高度分布和开发特性）
    + 激励（资源提供带宽、储存和计算资源）
### Process communication
+ 进行通信的实际上是进程（process），可被认为端系统中的一个程序
+ 进程与计算机网络之间的接口
  + 进程通过一个称为套接字（socket）的软件接口向网络发送报文和从网络接受报文
  
### Data integrity, Throughput, Timing and security
![](截图/1.png)

### TCP service and UDP service
+ TCP
  + reliable transport
  + flow control
  + congestion control
  + connection-oriented
+ UDP
  + unreliable data transfer

![](截图/2.png)

### DNS
+ **Domain Name System**
+ app-layer
+ a distributed, hierarchical database
+ ![](截图/TIM图片20190923115607.png)
+ Root name servers(存着包含了host尾名为.com,.edu等等的TLD DNS server的ip地址)
  + 13 logical root name "servers" worldwide
  + each “server” replicated many times
+ TLD DNS server
+ iterated query:
![](截图/TIM图片20190923115000.png)
+ DNS records
    + RR format: (name, value, type, ttl)->RR means resource records
### DASH: Dynamic Adaptive Streaming over HTTP

+ server:
  + divides video file into multiple chunks each chunk stored, encoded at different rates
  + manifest file: provides URLs for different chunks
+ client:
  + periodically measures server-to-client bandwidth
consulting manifest, requests one chunk at a time
    + chooses maximum coding rate sustainable given current bandwidth
    + can choose different coding rates at different points in time (depending on available bandwidth at time)
+ “intelligence” at client: client determines
  + when to request chunk (so that buffer starvation, or
overflow does not occur)
  + what encoding rate to request (higher quality when
more bandwidth available)
  + where to request chunk (can request from URL server
that is “close” to client or has high available
bandwidth) 