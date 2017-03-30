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

"""Traffic script that sends an TCP or UDP packet
from one interface to the other.
"""

import sys
import ipaddress

from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.inet6 import IPv6
from scapy.all import Ether

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


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


class VxLANGPE(Packet):
    """define the vxlan-gpe protocol for the packet analyse"""
    name = "vxlan-gpe"
    fields_desc=[XByteField("flags",0x0c),ShortField("reserved",0),
                 XByteField("nextproto",0x3),BitField("vni",0,24),
                 XByteField("reserved",0x0)]

class NSH(Packet):
    """define the NSH protocol for the packet analyse"""
    name = "NSH"
    fields_desc=[XBitField("flags",0x0,10),XBitField("length",0x6,6),
                 XByteField("MDtype",0x1),XByteField("nextproto",0x3),
                 XBitField("nsp",0x0,24),XBitField("nsi",0x0,8),
                 IntField("c1",0),IntField("c2",0),
                 IntField("c3",0),IntField("c4",0)]

def main():
    """Send TCP or UDP packet from one traffic generator interface to the other.
    """
    args = TrafficScriptArg(
        ['src_mac', 'dst_mac', 'src_ip', 'dst_ip', 'framesize'])

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    frame_size = args.get_arg('framesize')
    pad_len = int(frame_size) - (14 + 20 + 20 + 4)
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

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
               ip_version(src=src_ip, dst=dst_ip) /
               protocol(sport=int(source_port), dport=int(destination_port)) /
               Raw(load=pad_data))

    txq.send(pkt_raw)
    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError("TCP/UDP Rx timeout")

    ## expect a vxlan-gpe+nsh packet, begin to check it
    expect_pkt_len = frame_size + 74 - 4
    recv_pkt_len = len(ether)
    if recv_pkt_len < expect_pkt_len:
        raise RuntimeError("Receive packet size {0} too small".format(recv_pkt_len))

    if not ether.haslayer(IP):
        raise RuntimeError("Not the IPv4 packet")

    pkt_proto = ether[IP].proto
    if pkt_proto != UDP:
        raise RuntimeError("Not the UDP packet")

    dst_port = ether[UDP].dport
    if dst_port != 4790:
        raise RuntimeError("udp dest port must 4790")

    payload_data = ether[Raw].load
    
    ##get the vxlan-gpe packet and check it
    vxlangpe_pkt = VxLANGPE(payload_data[0:8])
    if vxlangpe_pkt.flags != 0xc:
        raise RuntimeError("Vxlan-gpe flags {0} incorrect".format(vxlangpe_pkt.flags))

    if vxlangpe_pkt.nextproto != 0x4:
        raise RuntimeError("next protocol not the NSH")

    if vxlangpe_pkt.vni != 9:
        raise RuntimeError("the VNI {0} incorrect".format(vxlangpe_pkt.vni))

    ##get the NSH packet and check it
    nsh_pkt = NSH(payload_data[8:32])
    if nsh_pkt.flags != 0x0:
        raise RuntimeError("NSH flags {0} incorrect".format(nsh_pkt.flags))

    if nsh_pkt.length != 0x6:
        raise RuntimeError("NSH length {0} incorrect".format(nsh_pkt.length))

    if nsh_pkt.MDtype != 0x1:
        raise RuntimeError("NSH MD-Type {0} incorrect".format(nsh_pkt.MDtype))

    if nsh_pkt.nextproto != 0x3:
        raise RuntimeError("NSH next protocol {0} incorrect".format(nsh_pkt.nextproto))

    if nsh_pkt.nsp != 185:
        raise RuntimeError("NSH Service Path ID {0} incorrect".format(nsh_pkt.nsp))

    if nsh_pkt.nsi != 255:
        raise RuntimeError("NSH Service Index {0} incorrect".format(nsh_pkt.nsi))

    if nsh_pkt.c1 != 3232248395:
        raise RuntimeError("NSH c1 {0} incorrect".format(nsh_pkt.c1))

    if nsh_pkt.c2 != 9:
        raise RuntimeError("NSH c2 {0} incorrect".format(nsh_pkt.c2))

    if nsh_pkt.c3 != 3232248392:
        raise RuntimeError("NSH c3 {0} incorrect".format(nsh_pkt.c3))

    if nsh_pkt.c4 != 50336437:
        raise RuntimeError("NSH c4 {0} incorrect".format(nsh_pkt.c4))

    ## we check all the fields about the vxlan-gpe + nsh, this test will pass
    sys.exit(0)


if __name__ == "__main__":
    main()
