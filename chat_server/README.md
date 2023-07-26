# CSCI 363 - Computer Networks



## Bucknell University
## Lewisburg, PA
# Project: CSCI363 Chat Server

# Student Info
Name: Taylor LaMantia

# Description
This program is a chat server for client communication with a server using TCP Server. The server can accept multiple simultaneous TCP connections from clients, can handle each client in its own thread using select or poll. The client can send messages to the server, which will broadcast the message to all connected clients. Server displays nickname of client along with message when broadcasting messge to other clients. Server handles disconnection of clients and updates list of connected clients accordingly. Server can handle a maximum of 100 clients at a time.

# Server Commands:

/nick \<nickname> - allows the client to set their nickname

/list - shows the list of connected clients

/quit - allows the client to disconnect from the chat

# Running the Program

To run the program type "python server.py \<PORT number>" to get the server running.
Once the server is running a new client can connect by typing "python client.py \<server HOST number> \<server PORT number>".
A message can then be input by the client in the terminal or one of the server commands.

Resources:
https://realpython.com/python-sockets/
https://learningactors.com/creating-command-line-based-chat-room-using-python/
https://docs.python.org/3/howto/sockets.html
https://python.plainenglish.io/create-a-basic-lan-chat-room-with-python-f334776bf70c
https://stackoverflow.com/questions/49330459/python-chat-server-version-command
