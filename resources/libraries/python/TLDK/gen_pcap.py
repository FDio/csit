#! /usr/bin/python
# Copyright (c) 2017 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module is used to generate pcap file used to execute UDP test cases.
"""

from scapy.layers.inet import Ether, IP, UDP, fragment
from scapy.layers.inet6 import IPv6
from scapy.utils import PcapWriter
from resources.libraries.python.TLDK.TLDKConstants import TLDKConstants as con

def create_packet(psz, is_ipv6, frag_size=None):
    """Create a packet to use scapy send to DUT."""
    if is_ipv6 != True:
        packet = Ether()/IP()/UDP()/("X" * psz)
        packet[IP].src = "192.168.1.56"
        packet[IP].dst = "192.168.1.233"
    else:
        packet = Ether()/IPv6()/UDP()/("X" * psz)
        packet[IPv6].src = "2001:4860:b002::56"
        packet[IPv6].dst = "2001:4860:b002::28"
    packet[Ether].src = "DE:AD:BE:EF:02:01"
    packet[Ether].dst = "DE:AD:BE:EF:01:02"
    packet[UDP].sport = 1111
    packet[UDP].dport = 32768
    if frag_size != None:
        packet = fragment(packet, fragsize=frag_size)
    return packet

def gen_ipv4_checksum_pcap():
    """Generate ipv4 checksum test case input pcap file."""
    writer = PcapWriter(con.TLDK_TESTCONFIG + "/test_ipv4_checksum_rx.pcap",
                        append=False)
    for i in range(1, 1474):
        packets = create_packet(i, False)
        for packet in packets:
            writer.write(packet)
    writer.close()

def gen_ipv6_checksum_pcap():
    """Generate ipv6 checksum test case input pcap file."""
    writer = PcapWriter(con.TLDK_TESTCONFIG + "/test_ipv6_checksum_rx.pcap",
                        append=False)
    for i in range(1, 1454):
        packets = create_packet(i, True)
        for packet in packets:
            writer.write(packet)
    writer.close()

def gen_ipv4_fragment_pcap():
    """Generate ipv4 fragment test case input pcap file."""
    writer = PcapWriter(con.TLDK_TESTCONFIG + "/test_ipv4_fragment_rx.pcap",
                        append=False)
    for i in range(1, 1474):
        packets = create_packet(i, False)
        for packet in packets:
            writer.write(packet)
    writer.close()

def gen_ipv6_fragment_pcap():
    """Generate ipv6 fragment test case input pcap file."""
    writer = PcapWriter(con.TLDK_TESTCONFIG + "/test_ipv6_fragment_rx.pcap",
                        append=False)
    for i in range(1, 1454):
        packets = create_packet(i, True)
        for packet in packets:
            writer.write(packet)
    writer.close()

def gen_ipv4_assemble_pcap():
    """Generate ipv4 assemble test case input pcap file."""
    writer = PcapWriter(con.TLDK_TESTCONFIG + "/test_ipv4_assemble_rx.pcap",
                        append=False)
    packets = create_packet(1066, False, 1024)
    for packet in packets:
        writer.write(packet)
    writer.close()

def gen_all_pcap():
    """Generate all test cases input pcap file."""
    gen_ipv4_checksum_pcap()
    gen_ipv6_checksum_pcap()
    gen_ipv4_fragment_pcap()
    gen_ipv6_fragment_pcap()
    gen_ipv4_assemble_pcap()

if __name__ == "__main__":
    gen_all_pcap()
