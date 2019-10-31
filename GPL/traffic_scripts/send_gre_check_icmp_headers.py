#!/usr/bin/env python

# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.

"""Traffic script that sends a GRE encapsulated ICMPv4 packet from one
interface to the other, where is expected ICMPv4 without GRE header.
"""

import sys

from robot.api import logger
from scapy.all import Ether
from scapy.layers.inet import IP_PROTOS
from scapy.layers.inet import IP
from scapy.layers.inet import ICMP
from scapy.layers.l2 import GRE

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


def main():
    args = TrafficScriptArg(
        ['tx_dst_mac', 'rx_dst_mac',
         'inner_src_ip', 'inner_dst_ip',
         'outer_src_ip', 'outer_dst_ip'])

    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    tx_dst_mac = args.get_arg('tx_dst_mac')
    rx_dst_mac = args.get_arg('rx_dst_mac')
    inner_src_ip = args.get_arg('inner_src_ip')
    inner_dst_ip = args.get_arg('inner_dst_ip')
    outer_src_ip = args.get_arg('outer_src_ip')
    outer_dst_ip = args.get_arg('outer_dst_ip')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    tx_pkt_raw = Ether(dst=tx_dst_mac) / \
        IP(src=outer_src_ip, dst=outer_dst_ip) / \
        GRE() / \
        IP(src=inner_src_ip, dst=inner_dst_ip) / \
        ICMP()

    sent_packets.append(tx_pkt_raw)
    txq.send(tx_pkt_raw)
    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError("ICMP echo Rx timeout")

    # Check RX headers
    if ether.dst != rx_dst_mac:
        raise RuntimeError("Matching of received destination MAC unsuccessful.")
    logger.debug("Comparison of received destination MAC: OK.")

    if ether['IP'].src != inner_src_ip:
        raise RuntimeError("Matching of received inner source IP unsuccessful.")
    logger.debug("Comparison of received outer source IP: OK.")

    if ether['IP'].dst != inner_dst_ip:
        raise RuntimeError(
            "Matching of received inner destination IP unsuccessful.")
    logger.debug("Comparison of received outer destination IP: OK.")

    if ether['IP'].proto != IP_PROTOS.icmp:
        raise RuntimeError("IP protocol is other than ICMP.")
    logger.debug("Comparison of received ICMP protocol: OK.")

    sys.exit(0)


if __name__ == "__main__":
    main()
