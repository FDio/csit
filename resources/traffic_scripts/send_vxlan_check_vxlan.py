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

import vxlan

from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    """Send IP ICMPv4/ICMPv6 packet from one traffic generator interface to
    the other one. Dot1q or Dot1ad tagging of the ethernet frame can be set.
    """
    args = TrafficScriptArg(['tx_src_mac', 'tx_dst_mac', 'tx_src_ip',
                             'tx_dst_ip', 'tx_vni', 'rx_src_ip', 'rx_dst_ip',
                             'rx_vni'])

    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    tx_src_mac = args.get_arg('tx_src_mac')
    tx_dst_mac = args.get_arg('tx_dst_mac')
    tx_src_ip = args.get_arg('tx_src_ip')
    tx_dst_ip = args.get_arg('tx_dst_ip')
    tx_vni = args.get_arg('tx_vni')
    rx_src_ip = args.get_arg('rx_src_ip')
    rx_dst_ip = args.get_arg('rx_dst_ip')
    rx_vni = args.get_arg('rx_vni')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    tx_pkt_p = (Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02') /
             IP(src='192.168.1.1', dst='192.168.1.2'))
    pkt_raw = (Ether(src=tx_src_mac, dst=tx_dst_mac) /
               IP(src=tx_src_ip, dst=tx_dst_ip) /
               UDP(sport=23456) /
               vxlan.VXLAN(vni=int(tx_vni)) /
               tx_pkt_p)

    # Send created packet on one interface and receive on the other
    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    ether = rxq.recv(2, ignore=sent_packets)

    # Check whether received packet contains layers Ether, IP and ICMP
    if ether is None:
        raise RuntimeError('Packet Rx timeout')
    ip = ether.payload

    if ip.src != rx_src_ip:
        raise RuntimeError('src mismatch')
    if ip.dst != rx_dst_ip:
        raise RuntimeError('dst mismatch')
    if ip.payload.dport != 4789:
        raise RuntimeError('udp dport mismatch')
    vxlan_pkt = ip.payload.payload

    if vxlan_pkt.vni != rx_vni:
        raise RuntimeError('vxlan mismatch')
    rx_pkt_p = vxlan_pkt.payload

    rx_pkt_p.src != tx_pkt_p.src
    rx_pkt_p.dst != tx_pkt_p.dst
    rx_pkt_p['IP'].src != tx_pkt_p['IP'].src
    rx_pkt_p['IP'].dst != tx_pkt_p['IP'].dst


    # if encaps_rx:
    #     if encaps_rx == 'Dot1q':
    #         if not vlan1_rx:
    #             vlan1_rx = vlan1
    #         if not ether.haslayer(Dot1Q):
    #             raise RuntimeError('Not VLAN tagged Eth frame received:\n{0}'
    #                                .format(ether.__repr__()))
    #         elif ether[Dot1Q].vlan != int(vlan1_rx):
    #             raise RuntimeError('Ethernet frame with wrong VLAN tag ({}) '
    #                                'received ({} expected):\n{}'.format(
    #                 ether[Dot1Q].vlan, vlan1_rx, ether.__repr__()))
    #     elif encaps_rx == 'Dot1ad':
    #         if not vlan1_rx:
    #             vlan1_rx = vlan1
    #         if not vlan2_rx:
    #             vlan2_rx = vlan2
    #         # TODO
    #         raise RuntimeError('Encapsulation {0} not implemented yet.'
    #                            .format(encaps_rx))
    #     else:
    #         raise RuntimeError('Unsupported/unknown encapsulation expected: {0}'
    #                            .format(encaps_rx))
    #
    # if not ether.haslayer(ip_format):
    #     raise RuntimeError('Not an IP packet received:\n{0}'
    #                        .format(ether.__repr__()))
    #
    # if not ether.haslayer(icmp_format):
    #     raise RuntimeError('Not an ICMP packet received:\n{0}'
    #                        .format(ether.__repr__()))

    sys.exit(0)

if __name__ == "__main__":
    main()
