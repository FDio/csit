#!/usr/bin/env python
# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""Traffic script that sends an VxLAN-GPE+NSH packet
from TG to DUT.
"""
import os
import sys
import ipaddress
import time
import socket

from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.inet6 import IPv6
from scapy.all import Ether, Packet, Raw
from scapy.utils import rdpcap
from scapy.all import sendp

from resources.libraries.python.SFC.TunnelProtocol import VxLAN 
from resources.libraries.python.constants import Constants as con
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg

from robot.api import logger

def valid_ipv4(ip):
    """Check if IP address has the correct IPv4 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv4 address format,
             otherwise return False.
    :rtype: bool
    """
    try:
        ipaddress.IPv4Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def valid_ipv6(ip):
    """Check if IP address has the correct IPv6 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv6 address format,
             otherwise return False.
    :rtype: bool
    """
    try:
        ipaddress.IPv6Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False

def check_nsh_sfc_proxy_inbound_packet(frame_size):
    """ check the packet is the Vxlan-gpe+nsh packet."""
    rx_pcapfile = '{0}/nsh_sfc_tests/sfc_scripts/temp_packet.pcap' \
                  .format(con.REMOTE_FW_DIR)

    logger.trace('read pcap file:{0}'.format(rx_pcapfile))

    packets = rdpcap(rx_pcapfile)
    if len(packets) < 1:
        raise RuntimeError("Not receive the packet!!")
        
    ether = packets[0]
    ## expect a vxlan packet, begin to check it
    expect_pkt_len = int(frame_size) - 24 - 4
    recv_pkt_len = len(ether)
    if recv_pkt_len != expect_pkt_len:
        raise RuntimeError("Receive packet size {0} not expect size {1}".
                           format(recv_pkt_len, expect_pkt_len))

    if not ether.haslayer(IP):
        raise RuntimeError("Not the IPv4 packet")

    pkt_proto = ether[IP].proto
    if pkt_proto != 17:
        raise RuntimeError("Not the UDP packet , {0}".format(pkt_proto))

    dst_port = ether[UDP].dport
    if dst_port != 4789:
        raise RuntimeError("udp dest port must 4789, {0}".format(dst_port))

    payload_data = ether[Raw].load
    
    ##get the vxlan packet and check it
    vxlan_pkt = VxLAN(payload_data[0:8])
    if vxlan_pkt.flags != 0x8:
        raise RuntimeError("Vxlan flags {0} incorrect".format(vxlan_pkt.flags))

    if vxlan_pkt.vni != 1:
        raise RuntimeError("the VNI {0} incorrect".format(vxlan_pkt.vni))

def main():
    """Send VxLAN-GPE+NSH packet from TG to DUT.
    """
    args = TrafficScriptArg(
        ['src_mac', 'dst_mac', 'src_ip', 'dst_ip', 'timeout', 'framesize'])

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    timeout = int(args.get_arg('timeout'))
    frame_size = int(args.get_arg('framesize'))
    pad_len = frame_size - (14 + 20 + 8 + 8 + 24 + 14 + 20 + 20 + 4)
    pad_data = "A" * pad_len

    protocol = TCP
    source_port = 1234
    destination_port = 5678

    ip_version = None
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        ip_version = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        ip_version = IPv6
    else:
        ValueError("Invalid IP version!")

    innerpkt = (Ether(src=src_mac, dst=dst_mac) /
               ip_version(src=src_ip, dst=dst_ip) /
               protocol(sport=int(source_port), dport=int(destination_port)) /
               Raw(load=pad_data))

    vxlangpe_nsh = '\x0c\x00\x00\x04\x00\x00\x09\x00\x00\x06' \
                   '\x01\x03\x00\x00\xb9\xff\xC0\xA8\x32\x4B' \
                   '\x00\x00\x00\x09\xC0\xA8\x32\x48\x03\x00\x12\xB5'

    raw_data = vxlangpe_nsh + str(innerpkt)

    pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
              ip_version(src=src_ip, dst=dst_ip) /
              UDP(sport=int(source_port), dport=4790) /
              Raw(load=raw_data))

    sendp(pkt_raw, iface=tx_if, count=3)

    time.sleep(timeout)

    ## let us begin to check the proxy inbound packet
    check_nsh_sfc_proxy_inbound_packet(frame_size)

    ## we check all the fields about the proxy inbound, this test will pass
    sys.exit(0)


if __name__ == "__main__":
    main()
