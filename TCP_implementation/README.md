# Final Project: Implementing TCP on Raw Sockets
## Team Members
Taylor LaMantia, Connor Vuocovich

## Description
The program attempted to implement TCP using raw sockets and do the following:
- Execute the 3-way handshake
- Implement some form of flow and congestion control 
- Reliable sliding window data exchange (ack/nack) with retransmissions and segment assembly (in-order)
- Proper TCP checksums
- Close the socket

## Implementation and Testing
The program is run by starting the echo server with “python3 echo-serv.py”
Lines 31-36 in socketTCP.py should be adjusted to contain the proper source and destination ports and addresses. 
Then run socketTCP.py.

## Issues
The 3-way handshake is somewhat successful, as a SYN is sent. However, there is an issue with the TCP checksum with the SYN-ACK that is received. The next ACK is sent but with a checksum error. Then the data packet is sent with the contents “Hello, TCP!”. As can be seen in Figure 4, the correct packet is sent and received back with the Hello, TCP! included, yet the issues with the checksum/header prevent the program from running properly

## Reflection
This project helped us gain a better understanding of the processes involved in TCP and how to use raw sockets. It also brought together all layers of the network, as these had to be linked in order to connect the sockets and send the packets. 
