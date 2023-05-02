import socket

HOST = 'localhost'  # or '127.0.0.1'
PORT = 8888

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'ping')
    data = s.recv(1024)

print('Received', data)