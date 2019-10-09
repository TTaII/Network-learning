# **Chapter 1**

- [**Chapter 1**](#chapter-1)
  - [## **Introduction**](#introduction)
    - [What is network?](#what-is-network)
    - [What is communication?](#what-is-communication)
    - [What applications require network access?](#what-applications-require-network-access)
    - [What network problems have you ever met in your real life?](#what-network-problems-have-you-ever-met-in-your-real-life)
    - [What is computer networking?](#what-is-computer-networking)
    - [Introductory course in computer netwoking(cn)](#introductory-course-in-computer-netwokingcn)
    - [How to use the textbook?](#how-to-use-the-textbook)
      - [For each lecture](#for-each-lecture)
      - [After each chapter](#after-each-chapter)
  - [+ read summary and interview if interested](#read-summary-and-interview-if-interested)
    - [A Top-Down Approach](#a-top-down-approach)
    - [Course overview](#course-overview)
    - [Other Readings](#other-readings)
  - [**roadmap**](#roadmap)
    - [1.1 What is the Internet: 'nuts and bolts' view](#11-what-is-the-internet-nuts-and-bolts-view)
      - [What is a protocols?](#what-is-a-protocols)
  - [+ all communication activity in Internet governed by protocols](#all-communication-activity-in-internet-governed-by-protocols)
    - [1.2 network edge](#12-network-edge)
      - [A closer look at network structure](#a-closer-look-at-network-structure)
        - [network edge:](#network-edge)
        - [network core:](#network-core)
      - [client/server model](#clientserver-model)
      - [peer-peer model](#peer-peer-model)
      - [keep in mind:](#keep-in-mind)
      - [Access net](#access-net)
      - [Physical media](#physical-media)
    - [**1.3 network core**](#13-network-core)
      - [**Internet core——packet-switching**](#internet-corepacket-switching)
      - [**Each packet maxmium to 1500 bytes and the size can be changed**](#each-packet-maxmium-to-1500-bytes-and-the-size-can-be-changed)
      - [**Two key network-core functions**](#two-key-network-core-functions)
      - [**Alternative core: circuit switching**](#alternative-core-circuit-switching)
      - [**Internet structure: network of network**](#internet-structure-network-of-network)
    - [**1.4 delay, loss, throughput in networks**](#14-delay-loss-throughput-in-networks)
      - [**Four sources of packet delay**](#four-sources-of-packet-delay)
      - [**Throughput**](#throughput)
    - [**1.5 protocol layers, service models**](#15-protocol-layers-service-models)
    - [**Network security**](#network-security)
## **Introduction**
---
### What is network?
+ social network
+ transportation
+ GPS
+ ...
### What is communication?
+ Base on two single nodes
+ Computer network consists of many communication network
### What applications require network access?
+ web browsing
+ online gaming
+ email
+ social applications
+ cloud storage
+ cloud computing
+ cloud server 
+ ...
### What network problems have you ever met in your real life?
+ prices
+ slow
+ 404 not found error
+ ...

Other name of this course: **Data communication and Computer networking** 

### What is computer networking?
+ A best known computer network is the Internet

### Introductory course in computer netwoking(cn)
+ learn principle of cn
+ learn practice of cn
+ Internet architecture/protocols as case study 

### How to use the textbook?
#### For each lecture
+ Read corresponding part after class
+ Go through the review questions
+ Write homework
#### After each chapter
+ read summary and interview if interested
---
### A Top-Down Approach
+ The top layer need the server of down layer
+ require -> layer -> target
+ 上面依赖下面，下面满足上面

### Course overview
+ intro: 2 classes
+ app layer: 3 classes
+ tran layer: 3 classes
+ net layer: 3 classes
+ link layer: 2 classes
+ wireless and mobile networks: 1 class

### Other Readings
[Lecture Video of this course in SUSTech](http://mooc1.chaoxing.com/course/95497722.html)

---
## **roadmap**
### 1.1 What is the Internet: 'nuts and bolts' view
+ <font color="red">host=end system</font>: PC,server,wireless labtop,smartphone
+ <font color="red">communication links</font>: fiber,copper,radio,satellite\
transmission rate: <font color="red">bandwidth</font>
+ <font color="red">Packet switches</font>: router and switch
+ <font color="red">ISPs</font>: Interconnected Internet service providers
+ <font color="red">Protocols</font>: TCP, IP, HTTP,Skype ...
+ <font color="red">Internet standands</font>: RFC(Request for comments), IETF(Internet Engineering Task Force)
+ <font color="red">Infrastructure</font>: web, voip, email, games

#### What is a protocols?
+ 交流之间的潜规则
+ The definition of msgs(format and order) and actions on msg transmission,receipt
+ all communication activity in Internet governed by protocols
---
### 1.2 network edge
#### A closer look at network structure
##### network edge:
+ hosts: clients and servers
+ access networks: mobile network, home network, institutional network
##### network core:
+ interconnected routers
+ network of networks
+ run app programs
+ e.g. web, email

#### client/server model
+ client host requests, receives service from always-on server
+ e.g. Web browser/server, email client/server

#### peer-peer model
+ minimal (or not) use of dedicated servers
+ Skype, Bit Torrent

#### keep in mind:
+ bandwidth(bits per second) of access network

#### Access net
+ Digital subscriber line(DSL)(Dedicated access to central office)
![](截图/TIM图片20190902151620.png)
+ cable network(frequency division multiplexing):happy:
+ ![](截图/TIM图片20190902151701.png)
+ home network
![](截图/TIM图片20190902151721.png)
+ Ethernet
![](截图/TIM图片20190902151740.png)
+ Wireless access networks
![](截图/TIM图片20190902151437.png)

#### Physical media
+ Guided media
>+ coax
>+ fiber
>+ radio
+ Unguided media
>+ radio  
### **1.3 network core**
#### **Internet core——packet-switching**
1. **router:**
> 1. Send and recive packet
> 2. Each packet transmitted at full link capacity
> 3. 上一个包经过transmission，下一个包就可以出发，不包括propagation
2.  **<u>store and forward:</u>** 
> 1. Entire packet must arrive at router before it can be transmitted on next link
> 2. Each time one bit and the first bit need to wait for the whole packet
3. **queuing and loss:**
> 1. If arrival rate (in bits) to link exceeds transmission rate of link for a period of time:
> 2. packets will queue, wait to be transmitted on link 
> 3. packets can be dropped (lost) if memory (buffer) fills up
#### **Each packet maxmium to 1500 bytes and the size can be changed**

#### **Two key network-core functions**
+ **forwarding:** move packets from router’s input to appropriate router output——>routing algorithms
+ **routing:** determines source-destination route taken by packets

#### **Alternative core: circuit switching**
1. TDM
2. FDM: 分频，频段越大，带宽越大，速度越快（路宽越大，流量越大）

####  **Internet structure: network of network**
+ ISP:
+ IXP:Internet exchange point
+ Content provider network: like baidu,  google, youtube（在用户附近建立data center ）
![](截图/TIM图片20190909113732.png)

### **1.4 delay, loss, throughput in networks**
#### **Four sources of packet delay**
* dnodal = dproc + dqueue + dtrans +  dprop
* dproc: nodal processing
>+ check bit errors 
>+ determine output link
>+ typically < msec
* dqueue: queueing delay 

#### **Throughput**
+ throughput: rate (bits/time unit) at which bits transferred between sender/receiver 
> + instantaneous: rate at given point in time 
> + average: rate over longer period of time
+ bottleneck link
> link on end-end path that constrains  end-end throughput 

### **1.5 protocol layers, service models**
### **Network security**

+ malware can get in host from: 
  + virus: self-replicating infection by receiving/executing  object (e.g., e-mail attachment) 
  + worm: self-replicating infection by passively receiving object that gets itself executed 
+ spyware malware can record keystrokes, web sites visited, upload info to collection site 
+ infected host can be enrolled in  botnet, used for spam. DDoS attacks

+ Bad guys can do:
  +  put malware into hosts via Internet
     + 病毒（需要交互），蠕虫（无需交互）  
  +  attack server, network infrastructure
     +  DoS————弱点攻击、带宽洪泛（向目标发送大量包）、连接洪泛（创建大量半开或全开的TCP连接）
  +  can sniff packets
     +  Wireshark
  +  can use fake addresses    
     +  IP spoofing(IP哄骗))
