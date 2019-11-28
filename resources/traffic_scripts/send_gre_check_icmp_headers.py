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
interface to the other, where is expected ICMPv4 without GRE header.
"""

import sys

from robot.api import logger
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP_PROTOS
from scapy.layers.inet import IP
from scapy.layers.inet import ICMP
from scapy.layers.l2 import GRE

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    args = TrafficScriptArg(
        [u'tx_dst_mac', u'rx_dst_mac',
         u'inner_src_ip', u'inner_dst_ip',
         u'outer_src_ip', u'outer_dst_ip'])

    tx_if = args.get_arg(u'tx_if')
    rx_if = args.get_arg(u'rx_if')
    tx_dst_mac = args.get_arg(u'tx_dst_mac')
    rx_dst_mac = args.get_arg(u'rx_dst_mac')
    inner_src_ip = args.get_arg(u'inner_src_ip')
    inner_dst_ip = args.get_arg(u'inner_dst_ip')
    outer_src_ip = args.get_arg(u'outer_src_ip')
    outer_dst_ip = args.get_arg(u'outer_dst_ip')

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
        raise RuntimeError(f'ICMP echo Rx timeout')

    # Check RX headers
    if ether.dst != rx_dst_mac:
        raise RuntimeError(f'Matching of received destination MAC unsuccessful.')
    logger.debug(f'Comparison of received destination MAC: OK.')

    if ether[u'IP'].src != inner_src_ip:
        raise RuntimeError(f'Matching of received inner source IP unsuccessful.')
    logger.debug(f'Comparison of received outer source IP: OK.')

    if ether[u'IP'].dst != inner_dst_ip:
        raise RuntimeError(
            f'Matching of received inner destination IP unsuccessful.')
    logger.debug(f'Comparison of received outer destination IP: OK.')

    if ether[u'IP'].proto != IP_PROTOS.icmp:
        raise RuntimeError(f'IP protocol is other than ICMP.')
    logger.debug(f'Comparison of received ICMP protocol: OK.')

    sys.exit(0)


if __name__ == "__main__":
    main()
