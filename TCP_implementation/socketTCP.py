import socket
import struct

# TCP flags
TCP_SYN = 0x02
TCP_ACK = 0x10
TCP_FIN = 0x01

# IP header fields
IP_VERSION = 4
IP_IHL = 5
IP_TOS = 0
IP_ID = 54321
IP_FLAGS = 0
IP_TTL = 255
IP_PROTOCOL_TCP = 6
IP_CHECKSUM = 0  # will be filled in later
IP_SOURCE = "127.0.0.1"  # replace with your source IP address
IP_DESTINATION = "127.0.0.1"  # replace with your destination IP address

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

# Create a raw socket
sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

# Set IP header fields
ip_header = struct.pack('!BBHHHBBH4s4s', (IP_VERSION << 4) + IP_IHL, IP_TOS, 0, IP_ID, (IP_FLAGS << 13), IP_TTL,
                        IP_PROTOCOL_TCP, IP_CHECKSUM, socket.inet_aton(IP_SOURCE), socket.inet_aton(IP_DESTINATION))

#Set the TCP SYN flag
TCP_FLAGS = TCP_SYN

# Set TCP header fields
tcp_header = struct.pack('!HHLLBBHHH', TCP_SOURCE_PORT, TCP_DESTINATION_PORT, TCP_SEQUENCE_NUMBER, TCP_ACK_NUMBER,
                         (TCP_DATA_OFFSET << 4) + 0, TCP_FLAGS, TCP_WINDOW_SIZE, TCP_CHECKSUM, TCP_URGENT_POINTER)

# Pack the IP and TCP headers
packet = ip_header + tcp_header

#Send the SYN packet
sock.sendto(packet, (IP_DESTINATION, TCP_DESTINATION_PORT))

# Receive the SYN-ACK packet
response_packet, addr = sock.recvfrom(1024)
tcp_header = response_packet[20:40]
TCP_FLAGS = int.from_bytes(tcp_header[13:14], byteorder='big')

# Extract the acknowledgement number from the SYN-ACK packet
TCP_ACK_NUMBER = int.from_bytes(tcp_header[4:8], byteorder='big')

#Set the TCP ACK flag
TCP_FLAGS = TCP_ACK

#Set the TCP header fields
tcp_header = struct.pack('!HHLLBBHHH', TCP_SOURCE_PORT, TCP_DESTINATION_PORT, TCP_SEQUENCE_NUMBER, TCP_ACK_NUMBER,
                         (TCP_DATA_OFFSET << 4) + 0, TCP_FLAGS, TCP_WINDOW_SIZE, TCP_CHECKSUM, TCP_URGENT_POINTER)

# Pack the IP and TCP headers
packet = ip_header + tcp_header

# Send the ACK packet
sock.sendto(packet, (IP_DESTINATION, TCP_DESTINATION_PORT))

# Data to send
data = b'Hello, TCP!'

# Calculate IP checksum
def calculate_checksum(data):
    if len(data) % 2:
        data += b'\x00'
    checksum = sum(struct.unpack('!H', data[i:i+2])[0] for i in range(0, len(data), 2))
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum = ~checksum & 0xffff
    return checksum

# Calculate TCP checksum
def calculate_tcp_checksum(ip_header, tcp_header, data=b''):
    psuedo_header = struct.pack('!4s4sBBH', socket.inet_aton(IP_SOURCE), socket.inet_aton(IP_DESTINATION), 0,
                                IP_PROTOCOL_TCP, len(tcp_header) + len(data))
    checksum_data = psuedo_header + tcp_header + data
    return calculate_checksum(checksum_data)

# Set IP checksum
IP_CHECKSUM = calculate_checksum(ip_header)

# Set TCP checksum
TCP_CHECKSUM = calculate_tcp_checksum(ip_header, tcp_header, data)

# Construct the packet
packet = ip_header + tcp_header + data

# Send the packet
sock.sendto(packet, (IP_DESTINATION, TCP_DESTINATION_PORT))
print('Packet sent successfully.')

# Receive the response
response, addr1 = sock.recvfrom(1024)
print('Response received.')
print(addr1)
print(response)

# Extract the TCP header and data from the response
ip_header_length = (struct.unpack('!B', response[0:1])[0] & 0x0F)

# Calculate the offset of the TCP header
tcp_header_offset = ip_header_length * 4

# Extract the TCP header and data from the response packet
tcp_header = response[tcp_header_offset:tcp_header_offset+20]
tcp_data = response[tcp_header_offset+20:]

# Extract the TCP flags from the TCP header
TCP_FLAGS = int.from_bytes(tcp_header[13:14], byteorder='big')

# Check if the SYN-ACK packet has the expected flags
if TCP_FLAGS != (TCP_SYN | TCP_ACK):
    print('Received unexpected flags in SYN-ACK packet.')
    exit()

# Extract the acknowledgement number from the TCP header
TCP_ACK_NUMBER = int.from_bytes(tcp_header[4:8], byteorder='big')

# Set the TCP header fields for the data packet
TCP_SEQUENCE_NUMBER += 1
TCP_ACK = 1
TCP_FLAGS = 0

# Set the TCP checksum for the data packet
TCP_CHECKSUM = calculate_tcp_checksum(ip_header, tcp_header, data)

# Pack the TCP header
tcp_header = struct.pack('!HHLLBBHHH', TCP_SOURCE_PORT, TCP_DESTINATION_PORT, TCP_SEQUENCE_NUMBER, TCP_ACK_NUMBER,
                         (TCP_DATA_OFFSET << 4) + 0, TCP_FLAGS, TCP_WINDOW_SIZE, TCP_CHECKSUM, TCP_URGENT_POINTER)

# Construct the packet
packet = ip_header + tcp_header + data

# Send the packet
sock.sendto(packet, (IP_DESTINATION, TCP_DESTINATION_PORT))
print('Data packet sent successfully.')

# Receive the response
response, addr2 = sock.recvfrom(1024)
print('Response received.')
print(addr2)
print(response)

# Close the socket
sock.close()