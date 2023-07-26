# Computer Networks
## Student Information
Taylor LaMantia

Bucknell University

BS Computer Engineering, BME Management (Spring 2024 Graduation)

## Description

This repository contains programs written for CSCI 363, Computer Networks, a class focused on the 7-layer network and 
principles and design of networked computing systems and application programs. 
The programs cover:

- Networked applications
- Network architecture
- Transport protocols
- Congestion control and resource allocation
- Internet working, addressing, error reporting, and routing
- Error detection, error connection, and medium access control
- Packet switching
- Fundamentals of network security

# tcp-udp_benchmark/
This program is an echo server (echo-server.py) and traffic generator (traffic-generator.py) that is used to evaluate the
performance of TCP vs UDP. Instructions for running and further details are included in the project folder.

# rtp/
This program is a reliable transport protocol. It uses file transfer over a UDP proxy server. It delivers a file from the sender 
to receiver over a lossy medium that has varying rate limit, drops, duplicates, reorders, and modifies packets. Instructions for running
and further details are included in the project folder.

# chat_server/
This program is a chat server for client communication with a server using TCP Server. The server can accept multiple simultaneous
TCP connections from clients, can handle each client in its own thread using select or poll. The client can send messages to the 
server, which will broadcast the message to all connected clients. Server displays nickname of client along with message when broadcasting
messge to other clients. Server handles disconnection of clients and updates list of connected clients accordingly. Server can handle a 
maximum of 100 clients at a time. Instructions for running and further details are included in the project folder.

# TCP_implementation/
This project is a work in progress. It attempts to implement a TCP client library in Python, using a raw socket. The goal of the program is to make a connection to any 
standard TCP port and be able to exchange data using a raw socket.
Additionally, it should connect to any standard TCP server (echo, http, etc) and exchange messages.
It attempts to:
- Execute the 3-way handshake
- Implement flow and congestion control 
- Reliable sliding window data exchange (ack/nack) with retransmissions and segment assembly (in-order)
- Proper TCP checksums
- Close the socket

