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

from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS

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


def main():
    """Send TCP or UDP packet from one traffic generator interface to the other.
    """
    args = TrafficScriptArg([u'tx_mac', u'rx_mac', u'src_ip', u'dst_ip', 
                             u'protocol', u'source_port', u'destination_port'])

    src_mac = args.get_arg(u'tx_mac')
    dst_mac = args.get_arg(u'rx_mac')
    src_ip = args.get_arg(u'src_ip')
    dst_ip = args.get_arg(u'dst_ip')
    tx_if = args.get_arg(u'tx_if')
    rx_if = args.get_arg(u'rx_if')

    protocol = args.get_arg(u'protocol')
    source_port = args.get_arg(u'source_port')
    destination_port = args.get_arg(u'destination_port')

    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        ip_version = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        ip_version = IPv6
    else:
        ValueError(f'Invalid IP version!')

    if protocol.upper() == u'TCP':
        protocol = TCP
    elif protocol.upper() == u'UDP':
        protocol = UDP
    else:
        raise ValueError(f'Invalid protocol type!')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
               ip_version(src=src_ip, dst=dst_ip) /
               protocol(sport=int(source_port), dport=int(destination_port)))

    txq.send(pkt_raw)

    while True:
        ether = rxq.recv(2)
        if ether is None:
            raise RuntimeError(u'TCP/UDP Rx timeout')

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if TCP in ether:
        print ("TCP packet received.")

    elif UDP in ether:
        print ("UDP packet received.")
    else:
        raise RuntimeError(f'Not an TCP or UDP packet '
                           f'received {ether.__repr__()}')

    sys.exit(0)


if __name__ == "__main__":
    main()
