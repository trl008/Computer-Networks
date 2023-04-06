# echo-client.py

import socket

HOST = '0.0.0.0'  # The server's hostname or IP address
PORT = 8888  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    while True:
        data = input("Type a message to send: ")
        if data == "quit":
            break
        data = data.encode('utf-8')
        s.sendto(data, (HOST, PORT))
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print(f"Received {data!r}")