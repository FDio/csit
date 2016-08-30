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

from scapy.layers.inet import ICMP, IP, UDP
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
        ['src_mac', 'dst_mac', 'src_ip', 'dst_ip'])

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')

    txq = TxQueue(tx_if)
    sent_packets = []
    ip_format = ''
    pkt_raw = ''
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                   IP(src=src_ip, dst=dst_ip) /
                   UDP())
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                   IPv6(src=src_ip, dst=dst_ip) /
                   ICMPv6EchoRequest())
    else:
        raise ValueError("IP not in correct format")

    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    sys.exit(0)


if __name__ == "__main__":
    main()
