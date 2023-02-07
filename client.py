'''
Program: client.py
Author: Taylor LaMantia

Chat server for client communication with server using TCP. Server can accept multiple simultaneous TCP connections from clients.
Server can handle each client in its own thread using select or poll. Client can send messages to the server, which will broadcast the 
message to all connected clients. Server displays nickname of client along with message
when broadcasting message to other clients. Server handles disconnection of clients and updates
list of connected clients accordingly. Server can handle a maximum of 100 clients at a time.

Server commands:
/nick <nickname> - allows the client to set their nickname
/list - shows the list of connected clients
/quit - allows the client to disconnect from the chat

To run the program type "python server.py <PORT number>" to get the server running.
Once the server is running a new client can connect by typining "python client.py <server HOST number> <server PORT number>".
A message can then be input by the client in the terminal or one of the server commands.

'''
# echo-client.py

import socket
import sys
import os
import threading

HOST = sys.argv[1]  # The server's hostname or IP address
PORT = int(sys.argv[2])  # The port used by the server

def handle_server(server_socket):
    while True:
        data = server_socket.recv(1024).decode()
        print(data)

# Set up the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Get the nickname from the user
nickname = input("Enter your nickname: ")
client_socket.send(nickname.encode())

# Start a new thread for handling incoming data from the server
thread = threading.Thread(target=handle_server, args=(client_socket,))
thread.start()

message = input("Enter a message to send or a server command: ")
client_socket.send(message.encode())
while True:
    message = input("")
    client_socket.send(message.encode())
