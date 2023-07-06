#!/usr/bin/python3
'''
COMP 332, Spring 2023
Code base for simple traceroute

Example usage:
   sudo python3 icmp_traceroute.py
'''

import socket
import struct
import sys

class IcmpTraceroute():

    def __init__(self, src_ip, dst_ip, ip_id, ip_ttl, icmp_id, icmp_seqno):

        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ip_id = ip_id
        self.max_ttl = ip_ttl
        self.ip_ttl = 1
        self.icmp_id = icmp_id
        self.icmp_seqno = icmp_seqno

        #self.run_traceroute(self)

    def run_traceroute(self):
        # emulate max hops from traceroute, up to 64 hops until destination is
        # reached
        print("traceroute to " +str(self.dst_ip)+', '+str(self.max_ttl) +'hops max')
        for ttl in range(1, self.max_ttl+1):

            # Create packet

            # we choose to calc checksum by creating a dummy header
            # we will use the fields in the dummy header to generate number,
            # each checksum number will with the ttl

            # create dummy header with ttl and compute its checksum
            ip_headerDum = self.create_ip_header(ttl,0)
            ip_checksum = self.checksum(ip_headerDum)
            # use computed checksum in 'real' ipheader
            ip_header = self.create_ip_header(ttl, ip_checksum)

            # create dummy hdr and compute its checksum
            icmp_headerDum = self.create_icmp_header()
            icmp_checksum = self.checksum(icmp_headerDum)
            # use computed checksum
            icmp_header = self.create_icmp_header(icmp_checksum)
            # strcutre hdr so that the first (20) bytes are ip hdr and the last
            # (8) bytes are icmp
            bin_echo_req = ip_header + icmp_header

            # Create send and receive sockets
            send_sock = socket.socket(
                socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            recv_sock = socket.socket(
                socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

            # Set IP_HDRINCL flag so kernel does not rewrite header fields
            send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

            # Set receive socket timeout to 2 seconds
            recv_sock.settimeout(2.0)

            start = time.time()
            # Send packet to destination
            send_sock.sendto(bin_echo_req, (self.dst_ip, 0))
            # Receive icmp reply (hopefully)
            [bin_echo_reply, addr] = recv_sock.recvfrom(1024)
            end = time.time()

            # Extract info from ip_header
            [ip_header_length, ip_identification, ip_protocol,
                ip_src_addr]  = self.decode_ip_header(bin_echo_reply)
            print(str(ttl)+" "+str(ip_src_addr)+" "+str((end-start)*1000)+" ms")

            # Extract info from icmp_header
            [icmp_type, icmp_code] = self.decode_icmp_header(
                bin_echo_reply, ip_header_length)

    def checksum(self, header_object):
        # goal is to compute a number representative of the contents of the
        # header

        tot = 0
        # in the event packet loss occurs
        if header_object == None:
            return tot

        # store info into 16 bits, collect hdrs elets in pairs of two
        for i in range(0,len(header_object),2):
            # shift 8 bits to the left
            tot += (header_object[i]<<8)+header_object[i+1]
        # all of the bits beyond the 1st 16 are overflow
        overflow = tot>>16
        # convert tot to int
        int16 = tot & 0xffff
        return overflow+int16

    def create_ip_header(self, ttl, checksum):

        # Returned IP header is packed binary data in network order

        # IP Header info from https://tools.ietf.org/html/rfc791
        ip_version = 4                                          # 4 bits
        ip_IHL = 5                                              # 4 bits
        # fit into a header field of at least 8 bits in size
        ip_verIHL = (ip_version << 4) + ip_IHL                  ## 8 bits  -B
        ip_tos = 0                                              ## 8 bits  -B
        ip_tlen = 0                                             ## 16 bits -H
        ip_identification = self.ip_id                          ## 16 bits -H
        ip_flags = 0                                            # 3 bits
        ip_fragment_offset = 0                                  # 13 bits
        # fit into a header field of size 16, 13 and 3 sized fields dne
        ip_flagsFrag = (ip_flags << 13) + ip_fragment_offset    ## 16 bits -H
        ip_ttl = ttl                                            ## 8 bits  -B
        ip_protocol = socket.IPPROTO_ICMP                       ## 8 bits  -B
        ip_checksum = checksum                                  ## 16 bits -H
        ip_sourceaddr = socket.inet_aton(self.src_ip)           ## 32 bits -4s
        ip_dstaddr = socket.inet_aton(self.dst_ip)              ## 32 bits -4s

        # B = 8 bits, H = 16 bits, 4s = 32 bits
        ip_header = struct.pack('!BBHHHBBH4s4s',
                ip_verIHL,
                ip_tos,
                ip_tlen,
                ip_identification,
                ip_flagsFrag,
                ip_ttl,
                ip_protocol,
                ip_checksum,
                ip_sourceaddr,
                ip_dstaddr
                )

        return ip_header

    def create_icmp_header(self, checksum):

        ECHO_REQUEST_TYPE = 8
        ECHO_CODE = 0

        # ICMP header info from https://tools.ietf.org/html/rfc792
        icmp_type = ECHO_REQUEST_TYPE      # 8 bits
        icmp_code = ECHO_CODE              # 8 bits
        icmp_checksum = checksum                  # 16 bits
        icmp_identification = self.icmp_id # 16 bits
        icmp_seq_number = self.icmp_seqno  # 16 bits

        # ICMP header is packed binary data in network order
        icmp_header = struct.pack('!BBHHH', # ! means network order
        icmp_type,           # B = unsigned char = 8 bits
        icmp_code,           # B = unsigned char = 8 bits
        icmp_checksum,       # H = unsigned short = 16 bits
        icmp_identification, # H = unsigned short = 16 bits
        icmp_seq_number)     # H = unsigned short = 16 bits

        return icmp_header

    def decode_ip_header(self, bin_echo_reply):

        # Decode ip_header
        # as we specified in run traceroute func, the first 20 bits (specified in
        # construction of ip_hdr) are 20 bits in length
        ip_header = struct.unpack('!BBHHHBBH4s4s',bin_echo_reply[:20])

        # Extract fields of interest
        ip_header_length = ip_header[0][4:8]
        ip_identification = ip_header[3]
        ip_protocol = ip_header[6]
        ip_src_addr = socket.inet_ntoa(ip_header[8])

        return [ip_header_length, ip_identification,
                ip_protocol, ip_src_addr]

    def decode_icmp_header(self, bin_echo_reply, ip_header_length):

        # Decode icmp_header
        # last 8 bits are the icmp hdr
        icmp_header = struct.unpack('!BBHHH', bin_echo_reply[ip_header_length:ip_header_length+8])

        # Extract fields of interest
        icmp_type = icmp_header[0] # Should equal 11, for Time-to-live exceeded
        icmp_code = icmp_header[1] # Should equal 0

        return [icmp_type, icmp_code]

def main():

    src_ip = '127.0.0.1' # Your IP addr (e.g., IP address of VM)
    dst_ip = '8.8.8.8'      # Destination IP address
    ip_id = 111             # IP header in wireshark should have
    ip_ttl = 64             # Max TTL
    icmp_id = 222           # ICMP header in wireshark should have
    icmp_seqno = 1          # Starts at 1, by convention

    if len(sys.argv) > 1:
        src_ip = sys.argv[1]
        dst_ip = sys.argv[2]
        ip_id = int(sys.arv[3])
        ip_ttl = int(sys.argv[4])
        icmp_id = int(sys.argv[5])
        icmp_seqno = int(sys.argv[6])

    traceroute = IcmpTraceroute(
            src_ip, dst_ip, ip_id, ip_ttl, icmp_id, icmp_seqno)
    traceroute.run_traceroute()

if __name__ == '__main__':
    main()

