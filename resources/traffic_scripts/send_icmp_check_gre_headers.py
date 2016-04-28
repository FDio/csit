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

"""Traffic script that sends an ip icmp packet
from one interface to the other.

If the packet has not arrived to the destination, the function will end
with return code 10
"""

import sys
import ipaddress

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from scapy.layers.inet import ICMP, IP
from scapy.layers.inet6 import IPv6
from scapy.all import Ether
from scapy.layers.inet6 import ICMPv6EchoRequest
from robot.api import logger


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
    except (ipaddress.AddressValueError, AttributeError):
        return False


def main():
    # TODO: documentation
    """TBD"""
    args = TrafficScriptArg(
        ['tx_if', 'rx_if',
         'tx_dst_mac', 'rx_dst_mac',
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
        IP(src=inner_src_ip, dst=inner_dst_ip) / \
        ICMP()

    sent_packets.append(tx_pkt_raw)
    txq.send(tx_pkt_raw)
    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError("ICMP echo Rx timeout")

    # if not ether.haslayer('IP'):
    #     raise RuntimeError(
    #         'Not an IP packet received {0}'.format(ether.__repr__()))

    # Check RX headers
    if ether.dst != rx_dst_mac:
        raise RuntimeError("Matching received destination MAC unsuccessful.")
    logger.debug("Comparing received destination MAC: OK.")

    if ether['IP'].src != outer_src_ip:
        raise RuntimeError("Matching received outer source IP unsuccessful.")
    logger.debug("Comparing received outer source IP: OK.")

    if ether['IP'].dst != outer_dst_ip:
        raise RuntimeError("Matching received outer destination IP unsuccessful.")
    logger.debug("Comparing received outer destination IP: OK.")

    if not ether['IP'].haslayer('GRE'):
        raise RuntimeError("Has no GRE header.")
    logger.debug("Comparing received GRE header: OK.")

    if ether['IP']['GRE']['IP'].src != inner_src_ip:
        raise RuntimeError("Matching received inner source IP unsuccessful.")
    logger.debug("Comparing received inner source IP: OK.")

    if ether['IP']['GRE']['IP'].dst != inner_dst_ip:
        raise RuntimeError("Matching received inner destination IP unsuccessful.")
    logger.debug("Comparing received inner destination IP: OK.")

    sys.exit(0)


if __name__ == "__main__":
    main()
