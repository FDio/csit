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

"""Traffic script that sends an IP ICMPv4/ICMPv6 packet from one interface to
the other one. Dot1q or Dot1ad tagging of the ethernet frame can be set.
"""

import sys
import ipaddress

from scapy.layers.l2 import Ether,  Dot1Q
from scapy.layers.inet import ICMP, IP
from scapy.layers.inet6 import IPv6, ICMPv6EchoRequest, ICMPv6ND_NS

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
    the other one. Dot1q or Dot1ad tagging of the ethernet frame can be set.
    """
    args = TrafficScriptArg([u'src_mac', u'dst_mac', u'src_ip', u'dst_ip'],
                            [u'encaps', u'vlan1', u'vlan2', u'encaps_rx',
                             u'vlan1_rx', u'vlan2_rx'])

    src_mac = args.get_arg(u'src_mac')
    dst_mac = args.get_arg(u'dst_mac')
    src_ip = args.get_arg(u'src_ip')
    dst_ip = args.get_arg(u'dst_ip')

    encaps = args.get_arg(u'encaps')
    vlan1 = args.get_arg(u'vlan1')
    vlan2 = args.get_arg(u'vlan2')
    encaps_rx = args.get_arg(u'encaps_rx')
    vlan1_rx = args.get_arg(u'vlan1_rx')
    vlan2_rx = args.get_arg(u'vlan2_rx')

    tx_if = args.get_arg(u'tx_if')
    rx_if = args.get_arg(u'rx_if')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []
    ip_format = u''
    icmp_format = u''
    # Create empty ip ICMP packet and add padding before sending
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        if encaps == u'Dot1q':
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       Dot1Q(vlan=int(vlan1)) /
                       IP(src=src_ip, dst=dst_ip) /
                       ICMP())
        elif encaps == u'Dot1ad':
            pkt_raw = (Ether(src=src_mac, dst=dst_mac, type=0x88A8) /
                       Dot1Q(vlan=int(vlan1), type=0x8100) /
                       Dot1Q(vlan=int(vlan2)) /
                       IP(src=src_ip, dst=dst_ip) /
                       ICMP())
        else:
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       IP(src=src_ip, dst=dst_ip) /
                       ICMP())
        ip_format = IP
        icmp_format = ICMP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        if encaps == u'Dot1q':
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       Dot1Q(vlan=int(vlan1)) /
                       IPv6(src=src_ip, dst=dst_ip) /
                       ICMPv6EchoRequest())
        elif encaps == u'Dot1ad':
            pkt_raw = (Ether(src=src_mac, dst=dst_mac, type=0x88A8) /
                       Dot1Q(vlan=int(vlan1), type=0x8100) /
                       Dot1Q(vlan=int(vlan2)) /
                       IPv6(src=src_ip, dst=dst_ip) /
                       ICMPv6EchoRequest())
        else:
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       IPv6(src=src_ip, dst=dst_ip) /
                       ICMPv6EchoRequest())
        ip_format = IPv6
        icmp_format = ICMPv6EchoRequest
    else:
        raise ValueError("IP(s) not in correct format")

    # Send created packet on one interface and receive on the other
    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    # Receive ICMP / ICMPv6 echo reply
    while True:
        ether = rxq.recv(2,)
        if ether is None:
            raise RuntimeError(u'ICMP echo Rx timeout')

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    # Check whether received packet contains layers IP/IPv6 and
    # ICMP/ICMPv6EchoRequest
    if encaps_rx:
        if encaps_rx == u'Dot1q':
            if not vlan1_rx:
                vlan1_rx = vlan1
            if not ether.haslayer(Dot1Q):
                raise RuntimeError(f'Not VLAN tagged Eth frame received:\n'
                                   f'{ether.__repr__()}')
            elif ether[Dot1Q].vlan != int(vlan1_rx):
                raise RuntimeError(f'Ethernet frame with wrong VLAN tag '
                                   f'({ether[Dot1Q].vlan}) u'
                                   f'received ({vlan1_rx} expected):\n'
                                   f'{ether.__repr__()}')
        elif encaps_rx == u'Dot1ad':
            if not vlan1_rx:
                vlan1_rx = vlan1
            if not vlan2_rx:
                vlan2_rx = vlan2
            # TODO
            raise RuntimeError(f'Encapsulation {encaps_rx} '
                               f'not implemented yet.')
        else:
            raise RuntimeError(f'Unsupported encapsulation expected: '
                               f'{encaps_rx}')

    if not ether.haslayer(ip_format):
        raise RuntimeError(f'Not an IP/IPv6 packet received:\n'
                           f'{ether.__repr__()}')

    if not ether.haslayer(icmp_format):
        raise RuntimeError(f'Not an ICMP/ICMPv6EchoRequest packet received:\n'
                           f'{ether.__repr__()}')

    sys.exit(0)


if __name__ == "__main__":
    main()
