import socket
import struct
from struct import *
import sys
import binascii
import time
import random
import re
import signal
import binascii
import subprocess

# TCP flags
TCP_SYN = 0x02
TCP_ACK = 0x10
TCP_FIN = 0x01

# IP header fields
IP_VERSION = 4
IP_IHL = 5
IP_TOS = 0
DONT_FRAGMENT = 0
FRAGMENT_STATUS = DONT_FRAGMENT
IP_PROTOCOL = socket.IPPROTO_TCP
IP_HDR_LEN = 20
IP_ID = 10001
IP_FLAGS = 0
IP_TTL = 255
IP_PROTOCOL_TCP = 6
IP_CHECKSUM = 0  # will be filled in later
IP_SOURCE = "10.0.2.15"  # replace with your source IP address
IP_DESTINATION = "10.0.2.15"  # replace with your destination IP address

# TCP header fields
TCP_SOURCE_PORT = 1234  # replace with your source port number
TCP_DESTINATION_PORT = 8888  # replace with your destination port number
TCP_SEQUENCE_NUMBER = 0
TCP_ACK_NUMBER = 0
TCP_DATA_OFFSET = 5
TCP_FLAGS = 0
TCP_WINDOW_SIZE = socket.htons(5840)
TCP_CHECKSUM = 0  # will be filled in later
TCP_URGENT_POINTER = 0
TCP_HDR_LEN = 20
RST_FLAG = 0

MIN_TOTAL_LENGTH = IP_HDR_LEN + TCP_HDR_LEN

def calculate_checksum(data):
    checksum = 0
    for index in range(0,len(data),2):
       		word = ((data[index]) << 8) + ((data[index+1]))
       		checksum = checksum + word
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum = ~checksum & 0xffff
    return checksum

# Create a raw socket
def create_sender_sock():
    try:
        sock_tx = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        # sock_tx.bind(("lo", socket.IPPROTO_IP))
    except (socket.error , event):
        print('Sender Raw socket could not be created. Error Code : ' + str(event[0]) + ' Notif ' + event[1])
        sys.exit()
    return sock_tx

# def create_receiver_sock():
#     try:
#         sock_rx = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_TCP)
#     except (socket.error , event):
#         print('Receiver raw socket sould not be created. Error Code : ' + str(event[0]) + ' Notif ' + event[1])
#         sys.exit()
#     return sock_rx

def build_IP_header(payload):
    checksum_hdr = 0
    total_len = 40+payload
    IHL_VERSION = IP_IHL + (IP_VERSION << 4)
    ip_header = struct.pack('!BBHHHBBH4s4s', IHL_VERSION, IP_TOS, total_len, IP_ID, FRAGMENT_STATUS, IP_TTL,IP_PROTOCOL, checksum_hdr, socket.inet_aton(IP_SOURCE), socket.inet_aton(IP_DESTINATION))
    checksum_hdr = calculate_checksum(ip_header)
    ip_header = struct.pack('!BBHHHBBH4s4s', IHL_VERSION, IP_TOS, total_len, IP_ID, FRAGMENT_STATUS, IP_TTL,IP_PROTOCOL, checksum_hdr, socket.inet_aton(IP_SOURCE), socket.inet_aton(IP_DESTINATION))
    return ip_header

def build_TCP_header(seq_no, ack_no, ackf, synf, finf=0, data= ""):
    # psuedo_header = struct.pack('!4s4sBBH', socket.inet_aton(IP_SOURCE), socket.inet_aton(IP_DESTINATION), 0,
#                                 IP_PROTOCOL_TCP, len(tcp_header) + len(data))
#     checksum_data = psuedo_header + tcp_header + data
#     return calculate_checksum(checksum_data)

    tcp_hdr_len = 5
    pushf, urgptr, temp_checksum, rstf, urgent_ptr = 0,0,0,0,0
    adv_window = socket.htons(1500)
    offset = (tcp_hdr_len << 4)
    tcp_flags = finf + (synf << 1) + (rstf << 2) + (pushf <<3) + (ackf << 4) + (urgent_ptr << 5)
    payload = len(data)
    if(payload % 2 == 1):
        payload = payload + 1	
    pack_arg = '!HHLLBBHHH'	
    if not data:							# For syn,ack,fin segments
        tcp_header = pack(pack_arg, TCP_SOURCE_PORT, TCP_DESTINATION_PORT, seq_no, ack_no, offset, tcp_flags, adv_window, temp_checksum, urgptr)	
    else:								# For segements that contain some payload
        pack_arg = pack_arg + str(payload) + 's'
        tcp_header = pack(pack_arg, TCP_SOURCE_PORT, TCP_DESTINATION_PORT, seq_no, ack_no, offset, tcp_flags,  adv_window, temp_checksum, urgptr,data)
    source_address = socket.inet_aton(IP_SOURCE)
    dest_address = socket.inet_aton(IP_DESTINATION)

    # Construct pseudo header for checksum calculation
    protocol = socket.IPPROTO_TCP
    rsrv_bits = 0
    tcp_length = len(str(tcp_header))
    pseudo_hdr = pack('!4s4sBBH', source_address, dest_address, rsrv_bits, protocol, tcp_length)
    pseudo_hdr = pseudo_hdr + tcp_header
    # tcp_checksum = calculate_checksum(pseudo_hdr)
    tcp_checksum = 0x9434
	#actual tcp header
    if not data:	
        tcp_header = pack(pack_arg, TCP_SOURCE_PORT, TCP_DESTINATION_PORT, seq_no, ack_no, offset, tcp_flags,  adv_window, tcp_checksum, urgptr)	
    else:
        tcp_header = pack(pack_arg, TCP_SOURCE_PORT, TCP_DESTINATION_PORT, seq_no, ack_no, offset, tcp_flags,  adv_window, tcp_checksum, urgptr,data)
    return tcp_header,20+payload

def get_received_packet(rx_sock):
    sourceIP = ""
    dest_port = ""
	# loop until we get the packet destined for our port and IP addr
    while ( sourceIP != str(IP_DESTINATION) and dest_port != str(TCP_SOURCE_PORT) or sourceIP != "" and dest_port != ""):
        recvPacket = rx_sock.recv(1024)
        ipHeader=recvPacket[0:20]
        ipHdr=unpack("!2sH8s4s4s",ipHeader)					#unpacking to get IP header
        sourceIP=socket.inet_ntoa(ipHdr[3])
        tcpHeader=recvPacket[20:40]						#unpacking to get TCP header
        tcpHdr=unpack('!HHLLBBHHH',tcpHeader)
        dest_port=str(tcpHdr[1])
        destinationIP = ""
        dest_port = ""
    return recvPacket

def check_ack_received(seq_no,ack_no,rx_sock,tcp_hdr_max = 40):
	
	recvPacket = get_received_packet(rx_sock)
	ipHdr=unpack("!2sH8s4s4s",recvPacket[0:20])
	mss = 0
	unpack_arg = '!HHLLBBHHH'
	if (tcp_hdr_max == 44):
		unpack_arg = unpack_arg + 'L'					# for syn-ack segment which is of 24 bytes
	tcpHdr=unpack(unpack_arg,recvPacket[20:tcp_hdr_max])
	length = ipHdr[1] - 40
	if (length == 0 or length == 4):					# length == 4 is for syn-ack segment
		seq_no_recv = tcpHdr[2]
		ack_no_recv = tcpHdr[3]
		tcp_flags = tcpHdr[5]
		if(tcp_hdr_max == 44):
			mss = tcpHdr[9]						# get MSS from SYN-ACK segment
		ack_flag = (tcp_flags & 16)
		if(ack_flag == 16 and ((seq_no == ack_no_recv - 1 and length == 4) or (seq_no == ack_no_recv and length == 0))):
			return seq_no_recv,mss
	return False,mss

# #Set the TCP SYN flag
# TCP_FLAGS = TCP_SYN

def perform_TCP_handshake(rx_sock,tx_sock):
    seq_no = 1
    ack_no = 0
    syn_flag = 1
    ack_flag = 0 
    tcp_seg,length = build_TCP_header(seq_no, ack_no, ack_flag,syn_flag)
    packet = build_IP_header(length) + tcp_seg
    print(packet)
    #Send the SYN packet
    tx_sock.sendto(packet, (IP_DESTINATION, TCP_DESTINATION_PORT))
    new_ack,mss = check_ack_received(seq_no,ack_no,rx_sock,44)
    if (new_ack == False):																# in case we dont receive our syn-ack
        print("handshake failed !\n")
        sys.exit()
    else:
        seq_no = 2									# send ack if we get our syn ack
        syn_flag = 0
        ack_flag = 1 	
        tcp_seg,length = build_TCP_header(seq_no, new_ack+1, ack_flag,syn_flag)
        packet = build_IP_header(length) + tcp_seg
        tx_sock.sendto(packet, (IP_DESTINATION, TCP_DESTINATION_PORT))
        return new_ack,2,mss


seq_no = 1
ack_no = 0
syn_flag = 1
ack_flag = 0 
sock_tx = create_sender_sock()
# sock_rx = create_receiver_sock()
tcp_seg,length = build_TCP_header(seq_no, ack_no, ack_flag,syn_flag)
packet = tcp_seg
# Send SYN
sock_tx.sendto(packet, (IP_DESTINATION, TCP_DESTINATION_PORT))
print("Sending SYN")

#Receive SYN-ACK
response, addr1 = sock_tx.recvfrom(1024)
print('SYN-ACK received at (address, port):' + str(addr1))

tcp_header = response[20:40]
TCP_FLAGS = int.from_bytes(tcp_header[13:14], byteorder='big')

# Extract the acknowledgement number from the SYN-ACK packet
TCP_ACK_NUMBER = int.from_bytes(tcp_header[4:8], byteorder='big')

# Set the TCP ACK flag
TCP_FLAGS = TCP_ACK

# Send back ACK that SYN-ACK was received
seq_no = 2
syn_flag = 0
ack_flag = 1 	
tcp_seg2,length = build_TCP_header(seq_no, TCP_ACK_NUMBER, ack_flag,syn_flag)
sock_tx.sendto(tcp_seg2, (IP_DESTINATION, TCP_DESTINATION_PORT))

# Send data
seq_no = 3
syn_flag = 0
ack_flag = 0 	
data = b'Hello, TCP!'
print('Data being sent: Hello, TCP!')
tcp_seg3,length = build_TCP_header(seq_no, TCP_ACK_NUMBER, ack_flag,syn_flag,0,data)
sock_tx.sendto(tcp_seg3, (IP_DESTINATION, TCP_DESTINATION_PORT))

#Receive data back from echo server
response2, addr2 = sock_tx.recvfrom(1024)
responseWord = response2[44:]
print(response2)
responseWord.decode()
# responseWord = struct.unpack('!HHLLBBHHH', response2)[9]
print('Response received at (address, port):' + str(addr2))
print('Resonse: '+ str(responseWord))

# Close the socket
sock_tx.close()