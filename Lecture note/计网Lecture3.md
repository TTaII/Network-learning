# Chapter 3
## 3.1 transport-layer services

## 3.2
+ demultiplexing
  + connectionless dem————UDP
  + connection-oriented dem————TCP
## 3.3 UDP
+ lost and out of order
+ No congestion control and no flow control
+ UDP header
  + source ip-16 bits
  + source port-16 bits
  + length-16 bits
  + checksum-16 bits
    + sum of all other 16bits except checksum and add it to checksum, if all 1 correct else wrong
    + checksum was calculated at the sender side
+ Reliable Data Transfer(rdt)
  + In top-10 list of important networking
  + rdt1.0 with reliable tranfer medium
    + directly send and accept
  + rdt2.0 channel with bit errors
    + two key mechanisms
      + error detection
      + feedback: control msgs(ACK,NAK)
  + rdt2.1 sender handles garbled ACK/NAKs
  + rdt2.2 NAK->(ACK 0 or ACK 1)
  + rdt3.0 Considering packet loss

## 3.4  principles of reliable data transfer
+ Go-Back-N receiver没有window
  + receiver
    +  只ack按顺序的seq包，乱序seq包都会按顺序排的最高seq包
  + sender
    + timeout(n): retransmit packet n and all higner seq# pkt in windows(直接发送全部window长度？直到nextseqnum==base+N)
    + ACK(n) means all pkts before pkts n are correctly received
    + 当没有接受到ACK包，或者接收到ACK以前的包，先ignore duplicate 的ACK， 然后等待timeout 发送duplicate ACK后面的包
    + 收到错的ACK，不理，等待某个包的timeout
    + 上层来包(即调用rdt_send(data))，先检查nextseqnum和base+N(即窗口剩余量)，如果nextseqnum大于等于base+N，说明窗口满了(N不够)，refuse_data
+ Selective repeat(选择重传) receiver有window
  + receiver构建buffer
    + send individual ACK for each pkt and maintain the buffer
  + sender
    + 哪个包timeout重传哪个
    + ACK(n) 就标记n as received if n 是当前窗口最小的seq，窗口往后推。
    + seq # size should be larger than window size (对的)
+ Comparison：
  + GBN has only timeout for oldest unacked packet
  + SR has timeout for each pkt
## 3.5  connection-oriented transport: TCP （出错的话，都只重传一个包）
### TCP seq. numbers, ACKs
+ sequence numbers
  + byte stream "number" of first byte in segment's data
+ acknowledgements
  + seq# of next byte expected from other side
  + cumulative ACK
### TCP segment structure
+ PPT 22
### TCP round trip time(RTT), timeout
+ timeout needs to longer than RTT but RTT varies
+ SampleRTT: measured time from current segment transmission until ACK
+ SampleRTT is not enough, need several recent measurement
+ EstimatedRTT = (1-a)*EstimatedRTT + a*SampleRTT
  + EstimatedRTT 包括了前t个RTT的计算
+ 任需要safety margin
  + DevRTT = (1-beta)*DevRTT + beta*|SampleRTT - EstimatedRTT|
  + TimeoutInterval = EstimatedRTT + 4*DevRTT(safety margin)(PPT 25)
### reliable data transfer
+ Retransmission triggered by timeout events or duplicate acks
+ delayed ACK
  + Wait up 500ms for next segment(已经有一个segment接收到了，等待500ms接受下一个，接收到立即回，相当于只用一个最新的ACK ack了两个)
+ cumulative ACK
  + sender 收到之后认为receiver已经收到以前的所有segment
+ duplicate ACK
  + 当receiver收到高于已收到segment的sequenceNumber（例如90+10=100），receiver只ACK100.
  + TCP fast retransmit: 当收到重复的duplicate ACK 3次，第四次收到?立即重传(即不用考虑timeout)(restart timer?)
+ updated ACK
  + lost 了其中一个，但是接受了后面几个进入receiver的buffer。所以发送duplicate ACK，当这个segment收到了，发送buffer里最大连续序列数的segment的updated ACK

### flow control
+ Important: receiver controls sender, so sender won’t overflow receiver’s buffer by transmitting too much, too fast
  + Action: receiver tell the sender to decrease the window size
  + sender limits amount of unacked (“in-flight”,在传输过程中的) data to receiver’s rwnd(receive里buffer的empty size) value 
  + To guarantee receive buffer will not overflow
### Connection management
+ Connection establishment
  + 三次挥手
+ Connection close
  + 四次握手
  + client: FIN
  + server: ACK
  + server: FIN(不能和上面的ACK一起是因为任然有data要发)
  + clinet: ACK

## 3.6 Principles of congestion control
+ Congestion
  + lost packets: the buffer of router(host network) overflow
  + long delays: queueing in router buffers
  + PPT 13~22

## 3.7 Congestion control
+ cwnd:(sender congestion window size)
+ sender limits transmission: LastBytesent-LastByteAcked<=cwnd
+ TCP sending rate: cwnd/RTT bytes/sec
+ approach: sender increases transmission rate(window size)
  + additive increase: increase cwnd by 1 MSS every RTT until loss detected
  + multiplicative decrease cut cwnd in half after loss
+ TCP Slow Start(慢启动)
  + initially cwnd = 1 MSS 速率为MSS/RTT
  + double cwnd every RTT when receiving ACK(每一个ACK增加一个MSS)
  + 当cwnd的值到达ssthresh时，状态转为拥塞避免
  + 超时导致的丢包事件-设置cwnd为1，重新开始慢启动，并且将ssthresh设置为cwnd的一半
  + 检测到三个冗余的ACK，状态转为快速恢复
+ TCP 拥塞避免(cwnd此时已经大于ssthresh)
  + cwnd+=(MSS/cwnd)*MSS for every RTT(因为每一个ACK是一个RTT，得ACK一个cwnd才加一个MSS，相当于ACK一个MSS增加一个MSS/cwnd)
  + 超时导致的丢包事件-设置cwnd为1，并且将ssthresh设置为cwnd的一半，状态转为慢启动
  + 检测到三个冗余的ACK，状态转为快速恢复
+ TCP 快速恢复
  + double cwnd every RTT when receiving ACK(每一个ACK增加一个MSS)(为了快点传输因duplicate ACK丢的包)
  + 超时导致的丢包事件-设置cwnd为1，并且将ssthresh设置为cwnd的一半，状态转为慢启动
+ TCP detecing, reacting to loss
  + loss by timeout(cwnd set to 1 MSS)
  + loss by 3 duplicate ACKs(cwnd is cut in half)
+ Summary: PPT 29~

