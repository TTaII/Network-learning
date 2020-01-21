# Chapter 7 Wireless and Mobile Network
+ Two important(but different) challenges
  + wireless: communication over wireless link
  + mobility: handling the mobile user who changes point of attachment to network
+ wireless does not mean mobility
+ Base station:
  + responsible for sending packets between wired network and wireless hosts in its "area"
  + e.g. cell towers(手机信号塔), 802.11 access points
+ infrastructure mode
  + base station connects mobiles into wired network
  + mobile can change base station 
+ ad hoc mode(自组织模式)(single hop: Bluetooth, ad hoc nets)
  + no base station
  + nodes can only transmit to other nodes within link coverage
  + route among themselves


## 7.2 Wireless links, characteristics
+ differences from wired link
  + decreased singal strength
+ CDMA
## 7.3 IEEE 802.11 wireless LANs("Wi-Fi")
+ 802.11b
  + 2.4-5GHz unlicensed spectrum(免许可频谱)
  + up to 11Mbps
  + direct sequence spread spectrum(DSSS) in physical layer
+ 802.11a
  + 5-6Ghz range
  + up to 54Mbps
+ 802.11g
  + 2.4-5Ghz range
  + up to 54Mbps
+ 802.11n(multiple antennae多单元天线)
  + 2.4-5GHz
  + up to 200Mbps
+ all above use CSMA/CA for multiple access
+ all have base station and ad-hoc network versions
+ Channels, association
  + 802.11b: 2.4GHz-2.485GHz spectrum divided into 11 channels at different frequencies
  + host: must associate with an AP
    + scans channels, listening for beacon frames(信标帧) containing AP's name(SSID) and MAC address
    + run DHCP to get ip address in AP's subnet
+ passive/active scanning
  + 主动：Probe Request frame from Host, Probe Response frame sent from APs(这个为主)
  + 被动：太浪费资源了
+ multiple access
  + CSMA/CA: no collision detection(很难去发现碰撞，因为信号衰减)
    + sender：
      + if sense channel idle for DIFS(Distributed Inter-frame Spacing) then transmit entire frame 
      + if busy，随机选择回退值
    + receiver: return ACK after SIFS(Short Inter-frame Spacing)
    + RTS(request-to-send) and CTS(clear-to-send，广播消息)可以允许sender反转channel，来获取发送long data frames 的权力
+ frame addressing(4个address)
  + First address: 接收端(wireless host, AP)的MAC
  + Second address: 发送端的MAC
  + Third：MAC of router interface to which AP is attached(路由器的MAC，可以是网关)
  + Forth：used only in ad hoc mode
  + 从AP到路由器-> 从802.11frame到802.3frame
+ 802.15：personal area network
## 7.4 Cellular Internet Access
+ 2G：voice 3G: (data+voice) 4G-LTE
## 7.5 Principles: addressing and routing to mobile users
+ No mobility-mobile wireless user using same AP
+ middle mobility-mobile user dis/connecting from network using DHCP
+ high mobility-mobile user pass through multiple AP while maintaining ongoing connections
+ indirect routing
  + home agent转发到新的foreign agent
  + mobile uses two addresses
    + permanent address:
    + care-of-address(转交地址):home agent用来转发路由的地址
  + inefficient when correspondent, mobile are in same network
+ direct routing
## 7.6 Mobile IP
## 7.7 Handling mobility in cellular networks
## 7.8 Mobility and higher-layer protocols
