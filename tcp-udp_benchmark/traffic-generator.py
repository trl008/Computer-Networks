import time
import random
import statistics
import argparse
import socket
import logging
import logging.config
import sys
import json
import struct
import numpy as np
import statistics

def en_logging():
    "setup loggers"
    #https://docs.python.org/3/howto/logging-cookbook.html
    logging.config.dictConfig(json.load(open('log_cfg.json', 'r')))

def parse_args():
    "Sets up the argument parser"
    parser = argparse.ArgumentParser(
        description="Traffic Generator."
    )
    parser.add_argument('--protocol',
                        help='The protocol to use [tcp].',
                        default='tcp',
                        choices=['tcp', 'udp'])
    parser.add_argument('--size',
                        default=10,
                        type=int,
                        help='Packet size [100] (in bytes).')
    parser.add_argument('--bandwidth',
                        help='The bandwidth in packets per second of the traffic.',
                        default=10,
                        type = int)
    parser.add_argument('--dst',
                        default = 'localhost',
                        help='Destination host, eg. hostname or 192.168.3.101 [localhost].')
    parser.add_argument('--port',
                        help='Port on destination host [8888].',
                        default=8888,
                        type=int)
    parser.add_argument('--distribution',
                        help='The distribution of packets to generate [burst].',
                        default='burst',
                        choices=['burst', 'uniform'])
    parser.add_argument('--duration',
                        help='The duration to run in seconds',
                        default=10,
                        type=int)
    return parser.parse_args()



def generate_packets(protocol, packet_size, bandwidth, distribution, duration, dst, port):
    """Generate network traffic of the specified protocol, packet size, bandwidth,
    distribution, and duration. Collect and display packet loss rate, out of order
    packet rate, and RTT."""
    print("Using "+ protocol + " to send and receive packets of size " + str(packet_size) + " to port " + str(port) + " at address " + dst + " at " + str(bandwidth) + " packets per second for " +str(duration) +  " seconds using " + distribution)
    
    if protocol == "tcp":
        sock_type = socket.SOCK_STREAM
    elif protocol == "udp":
        sock_type = socket.SOCK_DGRAM
    else:
        raise ValueError("Protocol must be 'tcp' or 'udp'")

    if distribution == "burst":
        interval = 1
    elif distribution == "uniform":
        interval = 1 / bandwidth
    else:
        raise ValueError("Distribution must be 'burst' or 'uniform'")

    packets_sent = 0
    packets_received = 0
    packets_lost = 0
    out_of_order_count = 0
    rtt_values = []


    with socket.socket(socket.AF_INET, sock_type) as sock:

        if protocol == "tcp":
            sock.connect((dst, port))

        
        start_time = time.time()

        # Run for the set duration of time
        while time.time() - start_time < duration:
            
            #Use burst distribution
            if distribution == "burst":
                format_string = f'>I{packet_size-4}s'
                for i in range(bandwidth):
                    packet_data = struct.pack(format_string, i, b'\0'*(packet_size-4))
                    
                    #Run on TCP protocol
                    if protocol == "tcp":
                        sock.send(packet_data)
                        send_time = time.time()
                        packets_sent+=1
                        try:
                            response_data, server = sock.recvfrom(packet_size+12)
                            recv_time=time.time()
                            print(response_data)
                            recv_sequence_number, zeros = struct.unpack(format_string,packet_data)
                            rtt = recv_time - send_time
                            rtt_values.append(rtt)
                            if recv_sequence_number != i:
                                out_of_order_count+=1
                            packets_received +=1
                        except socket.timeout:
                            print('Packet timed out')
                    
                    #Run on UDP protocol
                    elif protocol == "udp":
                        sock.sendto(packet_data, (dst, port))
                        send_time = time.time()
                        packets_sent+=1
                        try:
                            response_data, server = sock.recvfrom(packet_size+12)
                            recv_time=time.time()
                            print(response_data)
                            recv_sequence_number, zeros = struct.unpack(format_string,packet_data)
                            rtt = recv_time - send_time
                            rtt_values.append(rtt)
                            if recv_sequence_number != i:
                                out_of_order_count+=1
                            packets_received +=1
                        except socket.timeout:
                            print('Packet timed out')
                time.sleep(interval)

            #Use uniform distribution
            elif distribution == "uniform":
                format_string = f'>I{packet_size-4}s'
                for i in range(bandwidth):
                    packet_data = struct.pack(format_string, i, b'\0'*(packet_size-4))
                    
                    #Run over TCP 
                    if protocol == "tcp":
                        sock.send(packet_data)
                        send_time = time.time()
                        packets_sent+=1
                        try:
                            response_data, server = sock.recvfrom(packet_size+12)
                            recv_time=time.time()
                            print(response_data)
                            recv_sequence_number, zeros = struct.unpack(format_string,packet_data)
                            rtt = recv_time - send_time
                            rtt_values.append(rtt)
                            if recv_sequence_number != i:
                                out_of_order_count+=1
                            packets_received +=1
                            time.sleep(interval)
                        except socket.timeout:
                            print('Packet timed out')
                    
                    #Run over UDP
                    elif protocol == "udp":
                        sock.sendto(packet_data, (dst, port))
                        send_time = time.time()
                        packets_sent+=1
                        try:
                            response_data, server = sock.recvfrom(packet_size+12)
                            recv_time=time.time()
                            print(response_data)
                            recv_sequence_number, zeros = struct.unpack(format_string,packet_data)
                            rtt = recv_time - send_time
                            rtt_values.append(rtt)
                            if recv_sequence_number != i:
                                out_of_order_count+=1
                            packets_received +=1
                            time.sleep(interval)
                        except socket.timeout:
                            print('Packet timed out')
        #Close the socket
        sock.close()
                            
    total_time = time.time() - start_time

    packets_lost = packets_sent-packets_received
    loss_rate = (packets_lost/packets_sent)*100
    out_of_order_rate = out_of_order_count/packets_sent
    rtt_min = min(rtt_values)
    formatted_min = "{:.2e}".format(rtt_min)
    rtt_max = max(rtt_values)
    formatted_max = "{:.2e}".format(rtt_max)
    rtt_mean = np.mean(rtt_values)
    formatted_mean = "{:.2e}".format(rtt_mean)
    rtt_median = statistics.median(rtt_values)
    formatted_median = "{:.2e}".format(rtt_median)

    print("" + str(packets_sent) + " packets were sent and " + str(packets_received) + " packets received in " + str(total_time) + " seconds")
    print("Percent of packets lost: " + str(loss_rate) + "%") 
    print("Out of order packet rate: " + str(out_of_order_rate) + "%") 
    print(f"Minimum RTT: {formatted_min} seconds") 
    print(f"Maximum RTT: {formatted_max} seconds") 
    print(f"Mean RTT: {formatted_mean} seconds") 
    print(f"Median RTT: {formatted_median} seconds") 


if __name__ == "__main__":
    en_logging()
    # uncomment this to see every packet.
    args = parse_args()

    # look at those args
    logging.debug("Got args {}".format(args))

    generate_packets(args.protocol, args.size, args.bandwidth, args.distribution, args.duration, args.dst, args.port)