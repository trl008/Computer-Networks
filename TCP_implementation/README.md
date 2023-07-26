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

