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
from one interface to the other one.
"""

import sys

from scapy.all import Ether
from robot.api import logger
from scapy.layers.inet import ICMP, IP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    """Send IP ICMP packet from one traffic generator interface to the other."""
    args = TrafficScriptArg(
        ['tx_dst_mac', 'rx_src_mac', 'src_ip', 'dst_ip', 'rx_src_ip',
         'rx_src_ip_gw'])

    dst_mac = args.get_arg('tx_dst_mac')
    rx_src_mac = args.get_arg('rx_src_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    rx_src_ip = args.get_arg('rx_src_ip')
    rx_src_ip_gw = args.get_arg('rx_src_ip_gw')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    # Create empty ip ICMP packet
    pkt_raw = Ether(dst=dst_mac) / \
              IP(src=src_ip, dst=dst_ip) / \
              ICMP()

    # Send created packet on one interface and receive on the other
    txq.send(pkt_raw)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError("Ethernet frame Rx timeout")

    # ARP check
    if ether['ARP'] is not None:
        logger.trace("ARP matched")
    else:
        raise RuntimeError("Not an ARP packet received {0}"
                           .format(ether.__repr__()))

    # Compare data from packets
    if ether['ARP'].op == 1: # 1 - who-has request
        logger.trace("ARP request matched")
    else:
        raise RuntimeError("Matching packet unsuccessful: {0}"
                           .format(ether.__repr__()))

    if ether['ARP'].hwsrc == rx_src_mac:
        logger.trace("Source MAC matched")
    else:
        raise RuntimeError("Matching packet unsuccessful: {0}"
                           .format(ether.__repr__()))

    if ether['ARP'].hwdst == "00:00:00:00:00:00":
        logger.trace("Destination MAC matched")
    else:
        raise RuntimeError("Matching packet unsuccessful: {0}"
                           .format(ether.__repr__()))

    if ether['ARP'].psrc == rx_src_ip:
        logger.trace("Source ARP IP address matched")
    else:
        raise RuntimeError("Matching packet unsuccessful: {0}"
                           .format(ether.__repr__()))

    if ether['ARP'].pdst == rx_src_ip_gw:
        logger.trace("Destination ARP IP address matched")
    else:
        raise RuntimeError("Matching packet unsuccessful: {0}"
                           .format(ether.__repr__()))

    sys.exit(0)


if __name__ == "__main__":
    main()
