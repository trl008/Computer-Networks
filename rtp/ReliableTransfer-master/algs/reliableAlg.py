
import logging
import socket
import math
import os.path
import os
from algs.utils import load_file
from algs.udp_wrapper import UdpWrapper
from algs.texcept import TransferFailed
import zlib
import struct


from datetime import datetime, timedelta

log = logging.getLogger(__name__)

class ReliableAlg:
    def __init__(self, retries=3):
        self.retries = retries
        self.timeout = timedelta(seconds=5)

    def checksum_calculator(data):
        checksum = zlib.crc32(data)
        return checksum

    def run_server(self, outdir, addr, mtu):
        "run the server on the given addr/port/mtu, files are stored in outdir"
        # make sure directory exists
        os.makedirs(outdir, exist_ok=True)

        # create the socket to listen on
        sock = UdpWrapper(addr)

        # use blocking on the server.
        sock.setblocking(True)

        # bind the socket to the (address, port)
        sock.bind(addr)
        in_xfr = False
        outfile = None
        last = datetime.now() - self.timeout

        next_seq_num = 0

        log.info("Server started on {}".format(addr))
        while True:
            # wait for some data to arrive
            data,remote_addr = sock.recvfrom(mtu)

            if in_xfr and datetime.now() - last > self.timeout:
                # we got something but it's been too long, abort
                log.info("Abort transfer due to timeout.".format())
                in_xfr = False
                if outfile:
                    outfile.close()
                    outfile = None

            if in_xfr:
                # we are in a transfer, check for end of file
                if data[:9] == B"///END\\\\\\":
                    log.info("Done receiving file from {}.".format(
                        filepath, remote_addr))
                    in_xfr = False
                    outfile.close()
                    outfile = None
                    # let the client know we are done (ack the END message)
                    sock.sendto(B"OKEND", remote_addr)
                else:
                    # else we got a chunk of data
                    log.debug("Got a chunk!")

                    # extract header and compare the checksum from the header to the actual calculated checksum
                    udp_header = data[:8]
                    checksum_num = ReliableAlg.checksum_calculator(data[8:])
                    i, checksum = struct.unpack("II", udp_header)
                        
                    # send NACK if data is corrupted, if not, write data and send ACK
                    if (checksum_num == checksum) and (next_seq_num ==i):
                        # Just write data
                        outfile.write(data[8:])
                        sock.sendto(B'ACK', remote_addr)
                        next_seq_num +=1
                    elif (next_seq_num != i):
                        byte = struct.pack("I",next_seq_num)
                        sock.sendto(byte, remote_addr)
                    else:
                        sock.sendto(B'NACK', remote_addr)

            else:
                # we are not in a transfer, check for begin
                if data[:5] == B'BEGIN':

                    # parse the message to get mtu and filename
                    next_seq_num =0
                    smsg = data.decode('utf-8').split('\n')
                    beginmsg = smsg[0]
                    filename = smsg[1]
                    filepath = os.path.join(outdir, filename)

                    # check mtu
                    remote_mtu= int(beginmsg.split("/")[1])
                    if remote_mtu > mtu:
                        log.error("Cannot receive {} from {}, MTU({}) is too large.".format(
                            filepath, remote_addr, remote_mtu))
                        # send an error to the client
                        sock.sentdo(B'ERROR_MTU', remote_addr)
                    else:
                        log.info("Begin receiving file {} from {}.".format(
                            filepath, remote_addr))
                        outfile = open(filepath, 'wb')
                        in_xfr = True
                        # ack the begin message to the client
                        sock.sendto(B'OKBEGIN', remote_addr)
                else:
                    # we got something unexpected, ignore it.
                    log.info("Ignoring junk, not in xfer.")
            last = datetime.now()

    def begin_xfr(self, dest, filename, mtu):
        # create a socket to the destination (addr, port)
        sock = UdpWrapper(dest)

        #strip any path chars from filename for security
        filename = os.path.basename(filename)

        # timeout on recv after 1 second.
        sock.settimeout(1)
        tries = 0

        # retry until we get a response or run out of retries.
        while tries < self.retries:
            # construct the BEGIN message with MTU and filename
            msg = "BEGIN/{}\n{}".format(mtu, filename).encode('utf-8')

            # send the message
            sock.sendto(msg, dest)
            try:
                # wait for a response
                data, addr = sock.recvfrom(mtu)
            except socket.timeout:
                log.info("No response to BEGIN message, RETRY")
                tries += 1
                continue
            break
        # if we ran out of retries, raise an exception.
        if (tries >= self.retries):
            raise TransferFailed("No response to BEGIN message.")

        # if we got a response, make sure it's the right one.
        if data != B"OKBEGIN":
            raise TransferFailed("Bad BEGIN response from server, got {}".format(
                data
            ))

        # return the socket so we can use it for the rest of the transfer.
        return sock

    def end_xfr(self, sock, dest, mtu):
        # send the END message
        tries = 0
        while tries < self.retries:
            # send the message
            sock.sendto(B"///END\\\\\\", dest)
            try:
                # wait for a response
                data, addr = sock.recvfrom(mtu)
            except socket.timeout:
                log.info("No response to END message, RETRY")
                tries += 1
                continue
            break
        if (tries >= self.retries):
            raise TransferFailed("No response to END message.")
        # if we got a response, make sure it's the right one.
        if data != B"OKEND":
            raise TransferFailed("Bad END response from server, got {}".format(
                data
            ))

    def xfr(self, sock, payload, dest, mtu):
        # # send each chunk and header with checksum and seq num, waiting for an ACK
        i=0
        while i<len(payload):
            tries = 0
            while tries < self.retries:
                chunk = payload[i]
                log.info("Send chunk {} of {}".format(i, len(payload)-1))
                checksum = ReliableAlg.checksum_calculator(chunk)
                udp_header = struct.pack("II", i, checksum)
                packet_with_header = udp_header + chunk
                # send the chunk
                sock.sendto(packet_with_header, dest)
                try:
                    # wait for an ACK
                    data, addr = sock.recvfrom(mtu)
                except socket.timeout:
                    log.info("No response to CHUNK message, RETRY")
                    tries += 1
                    continue
                # if we got an ACK, break out of the loop (chunk was received)
                if data == B"ACK":
                    i+=1
                    break
                elif data == B"NACK":
                    log.info("Packet corrupted, RETRY")
                    continue
                elif data != B"NACK" or data != B"ACK":
                    if packet_with_header[0:4] != data:
                        i = struct.unpack("I", data)[0]
                        log.info("Wrong packet sent, RETRY")
                        continue
                else:
                    log.info("Bad response from server, got {} instead of ACK, RETRY".format(
                        data))
            if (tries >= self.retries):
                raise TransferFailed("No response to CHUNK message.")

    def chunk(self, payload, mtu):
        "break a payload into mtu sized chunks"
        # simple chunking by MTU
        chunks = math.ceil(len(payload) / mtu)
        return [payload[i*mtu:(i+1)*mtu] for i in range(chunks)], len(payload)

    def send_file(self, filename, dest, mtu):
        "Entrypoint for reliable alg  sending"
        st = datetime.now()
        log.info("Sending with reliable alg {} --> {}:{} [MTU={}].".format(
            filename, dest[0], dest[1], mtu))

        # break the file into mtu sized pieces
        payload, total_bytes = self.chunk(load_file(filename), mtu-8)

        # begin the transfer
        s = self.begin_xfr(dest, filename, mtu)

        # send the chunks
        self.xfr(s, payload, dest, mtu)

        # end the transfer
        self.end_xfr(s, dest, mtu)

        # print stats
        et = datetime.now()
        seconds = (et-st).total_seconds()
        log.info("Sent with reliable algorithm {} in {} seconds = {:.0f} bps.".format(
            filename, seconds,
            total_bytes / seconds))

        return True

    

# singleton
ra = ReliableAlg()