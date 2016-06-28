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

"""Traffic script that sends an IP ICMPv4/ICMPv6 packet from one interface
to the other. Source and destination IP addresses and source and destination
MAC addresses are checked in received packet.
"""

import sys
import ipaddress

from scapy.layers.inet import ICMP, IP
from scapy.layers.inet6 import IPv6
from scapy.all import Ether
from scapy.layers.inet6 import ICMPv6EchoRequest
from robot.api import logger

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def valid_ipv4(ip):
    try:
        ipaddress.IPv4Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def valid_ipv6(ip):
    try:
        ipaddress.IPv6Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def main():
    """Send IP ICMP packet from one traffic generator interface to the other."""
    args = TrafficScriptArg(
        ['tg_src_mac', 'tg_dst_mac', 'src_ip', 'dst_ip', 'dut_if1_mac',
         'dut_if2_mac'])

    src_mac = args.get_arg('tg_src_mac')
    dst_mac = args.get_arg('tg_dst_mac')
    dut1_if1_mac = args.get_arg('dut_if1_mac')
    dut1_if2_mac = args.get_arg('dut_if2_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []
    ip_format = ''
    pkt_raw = ''
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        pkt_raw = (Ether(src=src_mac, dst=dut1_if1_mac) /
                   IP(src=src_ip, dst=dst_ip) /
                   ICMP())
        ip_format = 'IP'
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        pkt_raw = (Ether(src=src_mac, dst=dut1_if1_mac) /
                   IPv6(src=src_ip, dst=dst_ip) /
                   ICMPv6EchoRequest())
        ip_format = 'IPv6'
    else:
        raise ValueError("IP not in correct format")

    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)
    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError("ICMP echo Rx timeout")
    if not ether.haslayer(ip_format):
        raise RuntimeError("Not an IP packet received {0}"
                           .format(ether.__repr__()))

    # Compare data from packets
    if src_ip == ether[ip_format].src and dst_ip == ether[ip_format].dst:
        logger.trace("IP matched")
        if dst_mac == ether['Ethernet'].dst and \
                dut1_if2_mac == ether['Ethernet'].src:
            logger.trace("MAC matched")
        else:
            raise RuntimeError("Matching packet unsuccessful: {0}"
                               .format(ether.__repr__()))
    else:
        raise RuntimeError("Matching packet unsuccessful: {0}"
                           .format(ether.__repr__()))
    sys.exit(0)


if __name__ == "__main__":
    main()
