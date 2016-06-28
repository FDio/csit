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

"""Traffic script that sends an IP ICMPv4/ICMPv6 packet
from one interface to the other one."""

import sys
import ipaddress

from scapy.layers.inet import ICMP, IP
from scapy.all import Ether
from scapy.layers.inet6 import ICMPv6EchoRequest
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Dot1Q

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def valid_ipv4(ip):
    """Check if IP address has the correct IPv4 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv4 address format,
    otherwise return false.
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
    otherwise return false.
    :rtype: bool
    """
    try:
        ipaddress.IPv6Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def main():
    """Send IP ICMPv4/ICMPv6 packet from one traffic generator interface to
    the other one.
    """
    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip'], ['encaps', 'vlan1', 'vlan2'])

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')

    encaps = args.get_arg('encaps')
    vlan1 = args.get_arg('vlan1')
    vlan2 = args.get_arg('vlan2')

    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []
    ip_format = ''
    icmp_format = ''
    # Create empty ip ICMP packet and add padding before sending
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        if encaps == 'Dot1q':
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       Dot1Q(vlan=int(vlan1)) /
                       IP(src=src_ip, dst=dst_ip) /
                       ICMP())
        elif encaps == 'Dot1ad':
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       Dot1Q(vlan=int(vlan1), type=0x88A8) /
                       Dot1Q(vlan=int(vlan2), type=0x8100) /
                       IP(src=src_ip, dst=dst_ip) /
                       ICMP())
        else:
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       IP(src=src_ip, dst=dst_ip) /
                       ICMP())
        ip_format = 'IP'
        icmp_format = 'ICMP'
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                   IPv6(src=src_ip, dst=dst_ip) /
                   ICMPv6EchoRequest())
        ip_format = 'IPv6'
        icmp_format = 'ICMPv6EchoRequest'
    else:
        raise ValueError("IP(s) not in correct format")

    # Send created packet on one interface and receive on the other
    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    ether = rxq.recv(2)

    # Check whether received packet contains layers Ether, IP and ICMP
    if ether is None:
        raise RuntimeError('ICMP echo Rx timeout')

    if not ether.haslayer(ip_format):
        raise RuntimeError('Not an IP packet received {0}'
                           .format(ether.__repr__()))

    if not ether.haslayer(icmp_format):
        raise RuntimeError('Not an ICMP packet received {0}'
                           .format(ether.__repr__()))

    sys.exit(0)

if __name__ == "__main__":
    main()
