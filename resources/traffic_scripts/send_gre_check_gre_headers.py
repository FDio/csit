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

"""Traffic script that sends a GRE encapsulated ICMPv4 packet from one
interface to the other, where GRE encapsulated packet is expected.
"""

import sys

from robot.api import logger
from scapy.all import Ether
from scapy.layers.inet import IP_PROTOS
from scapy.layers.inet import IP
from scapy.layers.inet import ICMP
from scapy.layers.l2 import GRE

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    args = TrafficScriptArg(
        ['tx_dst_mac', 'tx_src_mac', 'tx_outer_dst_ip', 'tx_outer_src_ip',
         'tx_inner_dst_ip', 'tx_inner_src_ip', 'rx_dst_mac', 'rx_src_mac',
         'rx_outer_dst_ip', 'rx_outer_src_ip'])

    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    tx_dst_mac = args.get_arg('tx_dst_mac')
    tx_src_mac = args.get_arg('tx_src_mac')
    tx_outer_dst_ip = args.get_arg('tx_outer_dst_ip')
    tx_outer_src_ip = args.get_arg('tx_outer_src_ip')
    tx_inner_dst_ip = args.get_arg('tx_inner_dst_ip')
    tx_inner_src_ip = args.get_arg('tx_inner_src_ip')
    rx_dst_mac = args.get_arg('rx_dst_mac')
    rx_src_mac = args.get_arg('rx_src_mac')
    rx_outer_dst_ip = args.get_arg('rx_outer_dst_ip')
    rx_outer_src_ip = args.get_arg('rx_outer_src_ip')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    tx_pkt_raw = Ether(dst=tx_dst_mac, src=tx_src_mac) / \
        IP(src=tx_outer_src_ip, dst=tx_outer_dst_ip) / \
        GRE() / \
        IP(src=tx_inner_src_ip, dst=tx_inner_dst_ip) / \
        ICMP()

    sent_packets.append(tx_pkt_raw)
    txq.send(tx_pkt_raw)
    ether = rxq.recv(2, ignore=sent_packets)

    if ether is None:
        raise RuntimeError("ICMP echo Rx timeout")

    # Check RX headers
    if ether.dst != rx_dst_mac:
        raise RuntimeError("Matching of received destination MAC unsuccessful.")
    logger.debug("Comparison of received destination MAC: OK.")

    if ether.src != rx_src_mac:
        raise RuntimeError("Matching of received source MAC unsuccessful.")
    logger.debug("Comparison of received source MAC: OK.")

    if ether['IP'].src != rx_outer_src_ip:
        raise RuntimeError("Matching of received outer source IP unsuccessful.")
    logger.debug("Comparison of received outer source IP: OK.")

    if ether['IP'].dst != rx_outer_dst_ip:
        raise RuntimeError(
            "Matching of received outer destination IP unsuccessful.")
    logger.debug("Comparison of received outer destination IP: OK.")

    if ether['IP'].proto != IP_PROTOS.gre:
        raise RuntimeError("IP protocol is no GRE.")
    logger.debug("Comparison of received GRE protocol: OK.")

    if ether['IP']['GRE']['IP'].src != tx_inner_src_ip:
        raise RuntimeError("Matching of received inner source IP unsuccessful.")
    logger.debug("Comparison of received inner source IP: OK.")

    if ether['IP']['GRE']['IP'].dst != tx_inner_dst_ip:
        raise RuntimeError(
            "Matching of received inner destination IP unsuccessful.")
    logger.debug("Comparison of received inner destination IP: OK.")

    sys.exit(0)


if __name__ == "__main__":
    main()
