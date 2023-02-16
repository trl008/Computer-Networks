'''
Program: server.py
Author: Taylor LaMantia

Chat server for client communication with server using TCP. Server can accept multiple simultaneous TCP connections from clients.
Server can handle each client in its own thread using select or poll. Client can send messages to the server, which will broadcast the 
message to all connected clients. Server displays nickname of client along with message
when broadcasting messge to other clients. Server handles disconnection of clients and updates
list of connected clients accordingly. Server can handle a maximum of 100 clients at a time.

Server commands:
/nick <nickname> - allows the client to set their nickname
/list - shows the list of connected clients
/quit - allows the client to disconnect from the chat

To run the program type "python server.py <PORT number>" to get the server running.
Once the server is running a new client can connect by typining "python client.py <server HOST number> <server PORT number>".
A message can then be input by the client in the terminal or one of the server commands.

'''

import sys
import os
import socket
import threading
import select

def handle_client(client_socket, client_address, nicknames):
    # Process the client's request
    nickname = client_socket.recv(1024).decode().strip()
    nicknames[client_socket] = nickname
    print("Connection accepted from", client_address, "with name", nickname)

    # Broadcast the new connection to all clients
    message = f"{nickname} has joined the chat!"
    broadcast(message, client_socket)

    while True:
        try:
            # Receive data from the client
            data = client_socket.recv(1024).decode().strip()
            
            # Handle the /nick command
            if data.startswith("/nick"):
                new_nickname = data.split(" ")[1]
                nicknames[client_socket] = new_nickname
                message = f"{nickname} is now known as {new_nickname}"
                nickname = new_nickname
                broadcast(message, client_socket)
                
            # Handle the /list command
            elif data == "/list":
                message = f"Connected clients: {', '.join(nicknames.values())}"
                client_socket.send(message.encode())
                
            # Handle the /quit command
            elif data == "/quit":
                client_socket.close()
                del nicknames[client_socket]
                message = f"{nickname} has left the chat."
                broadcast(message, client_socket)
                break
                
            # Broadcast the data to all connected clients
            else:
                message = f"{nickname}: {data}"
                broadcast(message, client_socket)
                message = f"Me: {data}"
                client_socket.send(message.encode())


        
        except:
            # Remove the client socket if there is a disconnection
            client_socket.close()
            del nicknames[client_socket]
            message = f"{nickname} has left the chat."
            broadcast(message, client_socket)
            break

def broadcast(message, sender_socket):
    for client_socket in nicknames:
        if client_socket != sender_socket:
            client_socket.send(message.encode())

clients = []
nicknames = {}

HOST = "0.0.0.0"  # All IP addresses on local machine 
PORT = int(sys.argv[1])  # Port to listen on (non-privileged ports are > 1023)

# Set up the server socket with the input host and port and 100 clients maximum
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(100)

# Use select to monitor the server socket for incoming connections
inputs = [server_socket]
while True:
    readable, _, _ = select.select(inputs, [], [])
  
    for socket in readable:
        # If the server socket is readable, it means there is a new connection
        if socket == server_socket:
            client_socket, client_address = server_socket.accept()
            inputs.append(client_socket)
            clients.append(client_socket)

            # Start a new thread for handling the new client
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address, nicknames))
            thread.start()
        # If a client socket is readable, it means the client has sent data
        else:
            # Find the corresponding nickname for the client socket
            nickname = nicknames.get(socket)
            # If the nickname is not found, it means the client has disconnected
            if nickname:
                # Call the handle_client function for this client
                handle_client(socket, None, nicknames)

    try:
        receive()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.closer()

        #shutdown all clients
        for client in clients:
            client.close()

        print("Server shut down.")
        exit(0)