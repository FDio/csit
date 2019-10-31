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

"""Traffic script that sends a UDP encapsulated into GRE packet from one
interface to the other, where GRE encapsulated packet is expected.
"""

import sys

from robot.api import logger
from scapy.all import Ether
from scapy.layers.inet import IP_PROTOS
from scapy.layers.inet import IP
from scapy.layers.inet import UDP
from scapy.layers.l2 import GRE

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


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
    udp_src = 1234
    udp_dst = 2345
    udp_payload = 'udp_payload'

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    tx_pkt_raw = Ether(dst=tx_dst_mac, src=tx_src_mac) / \
        IP(src=tx_outer_src_ip, dst=tx_outer_dst_ip) / \
        GRE() / \
        IP(src=tx_inner_src_ip, dst=tx_inner_dst_ip) / \
        UDP(dport=udp_dst, sport=udp_src) / \
        udp_payload

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
        raise RuntimeError("IP protocol is not GRE.")
    logger.debug("Comparison of received GRE protocol: OK.")

    if ether['IP']['GRE']['IP'].src != tx_inner_src_ip:
        raise RuntimeError("Matching of received inner source IP unsuccessful.")
    logger.debug("Comparison of received inner source IP: OK.")

    if ether['IP']['GRE']['IP'].dst != tx_inner_dst_ip:
        raise RuntimeError(
            "Matching of received inner destination IP unsuccessful.")
    logger.debug("Comparison of received inner destination IP: OK.")

    # check udp
    udp = ether['IP']['GRE']['IP']['UDP']
    if udp.dport != udp_dst:
        raise RuntimeError("UDP dport error {} != {}.".
                           format(udp.dport, udp_dst))
    print "UDP dport: OK."

    if udp.sport != udp_src:
        raise RuntimeError("UDP sport error {} != {}.".
                           format(udp.sport, udp_src))
    print "UDP sport: OK."

    if str(udp.payload) != udp_payload:
        raise RuntimeError("UDP payload check unsuccessful {} != {}.".
                           format(udp.payload, udp_payload))
    print "UDP payload: OK."

    sys.exit(0)


if __name__ == "__main__":
    main()
