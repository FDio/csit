#!/usr/bin/env python
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the u"License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an u"AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Traffic script that sends an IP ICMP packet
from one interface and expects ARP on the other one.
"""

import sys
import ipaddress

from scapy.layers.l2 import Ether
from scapy.layers.inet import ICMP, IP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def valid_ipv4(ip):
    u"""Check if IP address has the correct IPv4 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv4 address format,
             otherwise return False.
    :rtype: bool
    u"""
    try:
        ipaddress.IPv4Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def main():
    u"""Send IP ICMP packet from one traffic generator interface and expects
     ARP on the other."""
    args = TrafficScriptArg(
        [u'tx_dst_mac', u'rx_src_mac', u'tx_src_ip', u'tx_dst_ip', u'rx_arp_src_ip',
         u'rx_arp_dst_ip'])

    tx_dst_mac = args.get_arg(u'tx_dst_mac')
    rx_src_mac = args.get_arg(u'rx_src_mac')
    src_ip = args.get_arg(u'tx_src_ip')
    dst_ip = args.get_arg(u'tx_dst_ip')
    tx_if = args.get_arg(u'tx_if')
    rx_if = args.get_arg(u'rx_if')
    rx_dst_mac = u'ff:ff:ff:ff:ff:ff'
    rx_arp_src_ip = args.get_arg(u'rx_arp_src_ip')
    rx_arp_dst_ip = args.get_arg(u'rx_arp_dst_ip')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    # Create empty IP ICMP packet
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        pkt_raw = Ether(dst=tx_dst_mac) / IP(src=src_ip, dst=dst_ip) / ICMP()

    # Send created packet on one interface and receive on the other
    txq.send(pkt_raw)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError(f'Ethernet frame Rx timeout')

    if ether.dst == rx_dst_mac:
        print(f"Ethernet destination address matched.")
    else:
        raise RuntimeError(
            f'Matching ethernet destination address unsuccessful: '
            f'{ether.dst} != {rx_dst_mac}')

    if ether.src == rx_src_mac:
        print(f'Ethernet source address matched.')
    else:
        raise RuntimeError(
            f'Matching ethernet source address unsuccessful: '
            f'{ether.src} != {rx_src_mac}')

    # ARP check
    if ether[u'ARP'] is not None:
        print(f"ARP packet received.")
    else:
        raise RuntimeError(f'Not an ARP packet received {ether.__repr__()}')

    # Compare data from packets
    if ether[u'ARP'].op == 1:  # 1 - who-has request
        print(f"ARP request matched.")
    else:
        raise RuntimeError(f'Matching ARP request unsuccessful: '
                           f'{ether[u'ARP'].op} != {1}')

    if ether[u'ARP'].hwsrc == rx_src_mac:
        print(f"Source MAC matched.")
    else:
        raise RuntimeError(f'Matching Source MAC unsuccessful: '
                           f'{ether[u'ARP'].hwsrc} != {rx_src_mac}')

    if ether[u'ARP'].hwdst == u"00:00:00:00:00:00":
        print(f"Destination MAC matched.")
    else:
        raise RuntimeError(f'Matching Destination MAC unsuccessful: '
                           f'{ether[u'ARP'].hwdst} != {u"00:00:00:00:00:00"}'
                           .format(ether[u'ARP'].hwdst, u"00:00:00:00:00:00"))

    if ether[u'ARP'].psrc == rx_arp_src_ip:
        print(f"Source ARP IP address matched.")
    else:
        raise RuntimeError(
            f'Matching Source ARP IP address unsuccessful: '
            f'{ether[u'ARP'].psrc} != {rx_arp_src_ip}'
            .format(ether[u'ARP'].psrc, rx_arp_src_ip))

    if ether[u'ARP'].pdst == rx_arp_dst_ip:
        print(f"Destination ARP IP address matched.")
    else:
        raise RuntimeError(
            f'Matching Destination ARP IP address unsuccessful: '
            f'{ether[u'ARP'].pdst} != {rx_arp_dst_ip}')

    sys.exit(0)


if __name__ == u"__main__":
    main()
