"""
This echo-server is the server that accepts TCP or UDP packets 
on a specified port and echos them back to the sender as 
quickly as possible
"""

import socket
import argparse
import logging
import logging.config
import sys
import json

def en_logging():
    "setup loggers"
    #https://docs.python.org/3/howto/logging-cookbook.html
    logging.config.dictConfig(json.load(open('log_cfg.json', 'r')))

def start_tcp_echo_server(port, host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    print('Server listening on ', (host, port))
    conn, address = s.accept()
    with conn:
        print("Connected by ", host)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data)
            conn.sendall(data)

def start_udp_echo_server(port, host):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print('Server listening on ', (host,port))
    while s.fileno() != -1:
        try:
            data, address = s.recvfrom(1024)
            print(data)
            s.sendto(data, address)
        except socket.error:
            break
    s.close()
    print('Server stopped')


def parse_args():
    "Sets up the argument parser"
    parser = argparse.ArgumentParser(
        description="Traffic Server"
    )
    parser.add_argument('--protocol',
                        help='The protocol to use [tcp].',
                        default='tcp',
                        choices=['tcp', 'udp'])
    parser.add_argument('--port',
                        help='Port on destination host [8888].',
                        default=8888,
                        type=int)
    parser.add_argument('--host',
                        default = '0.0.0.0',
                        help='Local addres to listen on [0.0.0.0].')
    return parser.parse_args()

if __name__ == '__main__':
    en_logging()
    args = parse_args()


    # look at those args
    logging.debug("Got args {}".format(args))

    if args.protocol == 'tcp':
        print("Running on TCP")
        start_tcp_echo_server(args.port, args.host)
        
    elif args.protocol == 'udp':
        print("Running on UDP")
        start_udp_echo_server(args.port, args.host)
    else:
        print("Please specify either --protocol tcp or udp")
