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

"""Traffic script that sends an IP IPv4/IPv6 packet from one interface
to the other. Source and destination IP addresses and source and destination
MAC addresses are checked in received packet.
"""

import sys

import ipaddress
from robot.api import logger
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.layers.l2 import Ether, Dot1Q

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


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
    """Send IP/IPv6 packet from one traffic generator interface to the other."""
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
    vlan_rx = args.get_arg('vlan_rx')
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
        pkt_raw /= IP(src=src_ip, dst=dst_ip, proto=61)
        ip_format = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        pkt_raw /= IPv6(src=src_ip, dst=dst_ip)
        ip_format = IPv6
    else:
        raise ValueError("IP not in correct format")

    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    while True:
        if tx_if == rx_if:
            ether = rxq.recv(2, ignore=sent_packets)
        else:
            ether = rxq.recv(2)

        if ether is None:
            raise RuntimeError('IP packet Rx timeout')

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if rx_dst_mac == ether[Ether].dst and rx_src_mac == ether[Ether].src:
        logger.trace("MAC matched")
    else:
        raise RuntimeError("Matching packet unsuccessful: {0}".
                           format(ether.__repr__()))

    if encaps_rx == 'Dot1q':
        if ether[Dot1Q].vlan == int(vlan_rx):
            logger.trace("VLAN matched")
        else:
            raise RuntimeError('Ethernet frame with wrong VLAN tag ({}-'
                               'received, {}-expected):\n{}'.
                               format(ether[Dot1Q].vlan, vlan_rx,
                                      ether.__repr__()))
        ip = ether[Dot1Q].payload
    elif encaps_rx == 'Dot1ad':
        raise NotImplementedError()
    else:
        ip = ether.payload

    if not isinstance(ip, ip_format):
        raise RuntimeError("Not an IP packet received {0}".
                           format(ip.__repr__()))

    # Compare data from packets
    if src_ip == ip.src:
        logger.trace("Src IP matched")
    else:
        raise RuntimeError("Matching Src IP unsuccessful: {} != {}".
                           format(src_ip, ip.src))

    if dst_ip == ip.dst:
        logger.trace("Dst IP matched")
    else:
        raise RuntimeError("Matching Dst IP unsuccessful: {} != {}".
                           format(dst_ip, ip.dst))

    sys.exit(0)


if __name__ == "__main__":
    main()
