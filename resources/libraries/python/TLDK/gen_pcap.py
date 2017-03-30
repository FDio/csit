#! /usr/bin/python

import sys
from scapy.utils import *
from scapy.layers.inet import Ether,IP,UDP,TCP,fragment
from scapy.layers.inet6 import *

def create_packet(psz, is_ipv6, frag_size = None):
    if is_ipv6 != True:
        p = Ether()/IP()/UDP()/("X" * psz)
        p[IP].src = "192.168.1.56"
        p[IP].dst = "192.168.1.233"
    else:
        p = Ether()/IPv6()/UDP()/("X" * psz)
        p[IPv6].src = "2001:4860:b002::56"
        p[IPv6].dst = "2001:4860:b002::28"
    p[Ether].src = "DE:AD:BE:EF:02:01"
    p[Ether].dst = "DE:AD:BE:EF:01:02"
    p[UDP].sport = 1111
    p[UDP].dport = 32768
    if frag_size != None:
        p = fragment(p, fragsize=frag_size)
    return p

def gen_ipv4_checksum_pcap():
    writer = PcapWriter("./TLDK-tests/tldk_testconfig/test_ipv4_checksum_rx.pcap", append = False)
    for i in range(1, 1474):
        p = create_packet(i, False)
        for x in p:
            writer.write(x)
    writer.close()

def gen_ipv6_checksum_pcap():
    writer = PcapWriter("./TLDK-tests/tldk_testconfig/test_ipv6_checksum_rx.pcap", append = False)
    for i in range(1, 1454):
        p = create_packet(i, True)
        for x in p:
            writer.write(x)
    writer.close()

def gen_ipv4_fragment_pcap():
    writer = PcapWriter("./TLDK-tests/tldk_testconfig/test_ipv4_fragment_rx.pcap", append = False)
    for i in range(1, 1474):
        p = create_packet(i, False)
        for x in p:
            writer.write(x)
    writer.close()

def gen_ipv6_fragment_pcap():
    writer = PcapWriter("./TLDK-tests/tldk_testconfig/test_ipv6_fragment_rx.pcap", append = False)
    for i in range(1, 1454):
        p = create_packet(i, True)
        for x in p:
            writer.write(x)
    writer.close()

def gen_ipv4_assemble_pcap():
    writer = PcapWriter("./TLDK-tests/tldk_testconfig/test_ipv4_assemble_rx.pcap", append = False)
    p = create_packet(1066, False, 1024)
    for x in p:
        writer.write(x)
    writer.close()

def gen_all_pcap():
    gen_ipv4_checksum_pcap()
    gen_ipv6_checksum_pcap()
    gen_ipv4_fragment_pcap()
    gen_ipv6_fragment_pcap()
    gen_ipv4_assemble_pcap()

gen_all_pcap()
