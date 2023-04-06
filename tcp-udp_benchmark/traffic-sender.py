"""
Traffic sender. This creates a network traffic (packet) generator and can generate various types of 
network traffic. It uses initiates a traffic generator (traffic-generator.py).
Command line arguments to specify:
Protocol (TCP/UDP)
Packet size in bytes
Bandwidth (packets/second)
Distribution of packets (burst/uniform)
Duration

The sender also collects and reports the following metrics:
1. Loss rate (percent of packets lost)
2. Out of order packet rate (#ooo / total packets sent)
3. RTT (min/mean/median/max)
"""

import argparse
import socket
import logging
import logging.config
import sys
import json
import algs
from algs.texcept import TransferFailed

# custom exception
class AlgorithmNotImplementedError(NotImplementedError): pass

def en_logging():
    "setup loggers"
    #https://docs.python.org/3/howto/logging-cookbook.html
    logging.config.dictConfig(json.load(open('log_cfg.json', 'r')))

def parse_args():
    "Sets up the argument parser"
    parser = argparse.ArgumentParser(
        description="Traffic Sender"
    )
    parser.add_argument('--protocol',
                        default='tcp', nargs="+",
                        help="Protocol is [tcp].")
    parser.add_argument('--mtu',
                        default=100,
                        type=int,
                        help='Maximum transmition unit (MTU) (bytes) [100].')
    parser.add_argument('--bandwidth',
                        default = 'localhost',
                        help='Destination host, eg. hostname or 192.168.3.101 [localhost].')
    parser.add_argument('--port',
                        help='Port on destination host [8888].',
                        default=8888,
                        type=int)

    # add additional algorithms here.
    parser.add_argument('--alg',
                        help='The algorithm to use [sw].',
                        default='sw',
                        choices=['sw', 'ra'])
    return parser.parse_args()

if __name__ == "__main__":
    en_logging()
    # uncomment this to see every packet.
    # logging.getLogger("algs.udp_wrapper").setLevel(logging.DEBUG)
    args = parse_args()

    # look at those args
    logging.debug("Got args {}".format(args))

    if args.alg == 'sw': # stop and wait protocol
        # map files list into multiple calls
        try:
            result = list(map(lambda x: algs.sw.send_file(
                    filename=x,
                    dest=(args.dst, args.port),
                    mtu=args.mtu),
                args.files))
        except TransferFailed as x:
            logging.error("Transfer failed: {}".format(x))
            raise(x)
            sys.exit(-5)
    elif args.alg == 'ra': # reliableAlg protocol
        # map files list into multiple calls
        try:
            result = list(map(lambda x: algs.ra.send_file(
                    filename=x,
                    dest=(args.dst, args.port),
                    mtu=args.mtu),
                args.files))
        except TransferFailed as x:
            logging.error("Transfer failed: {}".format(x))
            raise(x)
            sys.exit(-5)
    else:
        raise AlgorithmNotImplementedError()
