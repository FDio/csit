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

"""Traffic script that sends an IP ICMPv4/ICMPv6 packet from one interface
to the other. Source and destination IP addresses and source and destination
MAC addresses are checked in received packet.
"""

import sys

import ipaddress
from robot.api import logger
from scapy.layers.inet import ICMP, IP
from scapy.layers.inet6 import ICMPv6EchoRequest
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether, Dot1Q

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


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
    except (AttributeError, ipaddress.AddressValueError):
        return False


def main():
    """Send IP ICMP packet from one traffic generator interface to the other."""
    args = TrafficScriptArg(
        ['tg_src_mac', 'tg_dst_mac', 'src_ip', 'dst_ip', 'dut_if1_mac',
         'dut_if2_mac'],
        ['encaps_tx', 'vlan_tx', 'vlan_outer_tx',
         'encaps_rx', 'vlan_rx', 'vlan_outer_rx'])

    tx_src_mac = args.get_arg('tg_src_mac')
    tx_dst_mac = args.get_arg('dut_if1_mac')
    rx_dst_mac = args.get_arg('tg_dst_mac')
    rx_src_mac = args.get_arg('dut_if2_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')

    encaps_tx = args.get_arg('encaps_tx')
    vlan_tx = args.get_arg('vlan_tx')
    vlan_outer_tx = args.get_arg('vlan_outer_tx')
    encaps_rx = args.get_arg('encaps_rx')
    vlan_rx = args.get_arg('vlan1_rx')
    vlan_outer_rx = args.get_arg('vlan_outer_rx')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []
    ip_format = ''
    pkt_raw = Ether(src=tx_src_mac, dst=tx_dst_mac)
    if encaps_tx == 'Dot1q':
        pkt_raw /= Dot1Q(vlan=int(vlan_tx))
    elif encaps_tx == 'Dot1ad':
        pkt_raw.type = 0x88a8
        pkt_raw /= Dot1Q(vlan=vlan_outer_tx)
        pkt_raw /= Dot1Q(vlan=vlan_tx)
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        pkt_raw /= IP(src=src_ip, dst=dst_ip)
        pkt_raw /= ICMP()
        ip_format = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        pkt_raw /= IPv6(src=src_ip, dst=dst_ip)
        pkt_raw /= ICMPv6EchoRequest()
        ip_format = IPv6
    else:
        raise ValueError("IP not in correct format")

    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)
    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError("ICMP echo Rx timeout")

    if rx_dst_mac == ether[Ether].dst and rx_src_mac == ether[Ether].src:
        logger.trace("MAC matched")
    else:
        raise RuntimeError(
            "Matching packet unsuccessful: {0}".format(ether.__repr__()))

    if encaps_rx == 'Dot1q':
        if ether[Dot1Q].vlan == int(vlan_rx):
            logger.trace("VLAN matched")
        else:
            raise RuntimeError('Ethernet frame with wrong VLAN tag ({}) '
                               'received ({} expected):\n{}'
                               .format(ether[Dot1Q].vlan, vlan_rx,
                                       ether.__repr__()))
        ip = ether[Dot1Q].payload
    elif encaps_rx == 'Dot1ad':
        # TODO: implement
        raise NotImplementedError()
    else:
        ip = ether.payload

    if not isinstance(ip, ip_format):
        raise RuntimeError(
            "Not an IP packet received {0}".format(ip.__repr__()))
    # Compare data from packets
    if src_ip == ip.src and dst_ip == ip.dst:
        logger.trace("IP matched")
    else:
        raise RuntimeError("Matching packet unsuccessful: {0}"
                           .format(ether.__repr__()))

    sys.exit(0)


if __name__ == "__main__":
    main()
