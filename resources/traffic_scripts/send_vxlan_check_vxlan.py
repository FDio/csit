#!/usr/bin/env python3
# Copyright (c) 2019 Cisco and/or its affiliates.
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

from scapy.layers.inet import IP, UDP, Raw
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
                IP(src='192.168.1.1', dst='192.168.1.2') /
                UDP(sport=12345, dport=1234) /
                Raw('rew data'))

    pkt_raw = (Ether(src=tx_src_mac, dst=tx_dst_mac) /
               IP(src=tx_src_ip, dst=tx_dst_ip) /
               UDP(sport=23456) /
               vxlan.VXLAN(vni=int(tx_vni)) /
               tx_pkt_p)

    # Send created packet on one interface and receive on the other
    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    ether = rxq.recv(2, ignore=sent_packets)

    # Check whether received packet contains layers Ether, IP and VXLAN
    if ether is None:
        raise RuntimeError('Packet Rx timeout')
    ip = ether.payload

    if ip.src != rx_src_ip:
        raise RuntimeError('IP src mismatch {} != {}'.format(ip.src, rx_src_ip))
    if ip.dst != rx_dst_ip:
        raise RuntimeError('IP dst mismatch {} != {}'.format(ip.dst, rx_dst_ip))
    if ip.payload.dport != 4789:
        raise RuntimeError('VXLAN UDP port mismatch {} != {}'.
                           format(ip.payload.dport, 4789))
    vxlan_pkt = ip.payload.payload

    if int(vxlan_pkt.vni) != int(rx_vni):
        raise RuntimeError('vxlan mismatch')
    rx_pkt_p = vxlan_pkt.payload

    if rx_pkt_p.src != tx_pkt_p.src:
        raise RuntimeError('RX encapsulated MAC src mismatch {} != {}'.
                           format(rx_pkt_p.src, tx_pkt_p.src))
    if rx_pkt_p.dst != tx_pkt_p.dst:
        raise RuntimeError('RX encapsulated MAC dst mismatch {} != {}'.
                           format(rx_pkt_p.dst, tx_pkt_p.dst))
    if rx_pkt_p['IP'].src != tx_pkt_p['IP'].src:
        raise RuntimeError('RX encapsulated IP src mismatch {} != {}'.
                           format(rx_pkt_p['IP'].src, tx_pkt_p['IP'].src))
    if rx_pkt_p['IP'].dst != tx_pkt_p['IP'].dst:
        raise RuntimeError('RX encapsulated IP dst mismatch {} != {}'.
                           format(rx_pkt_p['IP'].dst, tx_pkt_p['IP'].dst))

    # TODO: verify inner Ether()

    sys.exit(0)

if __name__ == "__main__":
    main()
