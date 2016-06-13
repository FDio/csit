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

"""Traffic script that sends an IP ICMP packet
from one interface and expects ARP on the other one.
"""

import sys
import ipaddress

from scapy.all import Ether
from scapy.layers.inet import ICMP, IP

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


def main():
    """Send IP ICMP packet from one traffic generator interface and expects
     ARP on the other."""
    args = TrafficScriptArg(
        ['tx_dst_mac', 'rx_src_mac', 'tx_src_ip', 'tx_dst_ip', 'rx_arp_src_ip',
         'rx_arp_dst_ip'])

    tx_dst_mac = args.get_arg('tx_dst_mac')
    rx_src_mac = args.get_arg('rx_src_mac')
    src_ip = args.get_arg('tx_src_ip')
    dst_ip = args.get_arg('tx_dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    rx_dst_mac = 'ff:ff:ff:ff:ff:ff'
    rx_arp_src_ip = args.get_arg('rx_arp_src_ip')
    rx_arp_dst_ip = args.get_arg('rx_arp_dst_ip')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    # Create empty IP ICMP packet
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        pkt_raw = Ether(dst=tx_dst_mac) / IP(src=src_ip, dst=dst_ip) / ICMP()

    # Send created packet on one interface and receive on the other
    txq.send(pkt_raw)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError("Ethernet frame Rx timeout")

    if ether.dst == rx_dst_mac:
        print("Ethernet destination address matched.")
    else:
        raise RuntimeError(
            "Matching ethernet destination address unsuccessful: {0} != {1}".
                format(ether.dst, rx_dst_mac))

    if ether.src == rx_src_mac:
        print("Ethernet source address matched.")
    else:
        raise RuntimeError(
            "Matching ethernet source address unsuccessful: {0} != {1}"
            .format(ether.src, rx_src_mac))

    # ARP check
    if ether['ARP'] is not None:
        print("ARP packet received.")
    else:
        raise RuntimeError("Not an ARP packet received {0}"
                           .format(ether.__repr__()))

    # Compare data from packets
    if ether['ARP'].op == 1:  # 1 - who-has request
        print("ARP request matched.")
    else:
        raise RuntimeError("Matching ARP request unsuccessful: {0} != {1}"
                           .format(ether['ARP'].op, 1))

    if ether['ARP'].hwsrc == rx_src_mac:
        print("Source MAC matched.")
    else:
        raise RuntimeError("Matching Source MAC unsuccessful: {0} != {1}"
                           .format(ether['ARP'].hwsrc, rx_src_mac))

    if ether['ARP'].hwdst == "00:00:00:00:00:00":
        print("Destination MAC matched.")
    else:
        raise RuntimeError("Matching Destination MAC unsuccessful: {0} != {1}"
                           .format(ether['ARP'].hwdst, "00:00:00:00:00:00"))

    if ether['ARP'].psrc == rx_arp_src_ip:
        print("Source ARP IP address matched.")
    else:
        raise RuntimeError(
            "Matching Source ARP IP address unsuccessful: {0} != {1}"
            .format(ether['ARP'].psrc, rx_arp_src_ip))

    if ether['ARP'].pdst == rx_arp_dst_ip:
        print("Destination ARP IP address matched.")
    else:
        raise RuntimeError(
            "Matching Destination ARP IP address unsuccessful: {0} != {1}"
            .format(ether['ARP'].pdst, rx_arp_dst_ip))

    sys.exit(0)


if __name__ == "__main__":
    main()
