#!/usr/bin/env python
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License');
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

"""Traffic script that sends an IPv4 ICMP packet with ID field and checks if
IPv4 is correctly encapsulated into IPv6 packet. Doing for ICMP echo request
and ICMP echo response packet."""

import sys

from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, ICMP, icmptypes

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def _is_ipv4_in_ipv6(pkt):
    """If IPv6 next header type in the given pkt is IPv4, return True,
    else return False. False is returned also if exception occurs."""
    ipv6_type = int(u'0x86dd', 16)  # IPv6
    try:
        if pkt.type == ipv6_type:
            if pkt.payload.nh == 4:
                return True
    except:  # pylint: disable=bare-except
        return False
    return False


def main():  # pylint: disable=too-many-statements, too-many-locals
    """Main function of the script file."""
    args = TrafficScriptArg([u'tx_dst_mac', u'tx_src_ipv4', u'tx_dst_ipv4',
                             u'tx_icmp_id', u'rx_dst_mac', u'rx_src_mac',
                             u'src_ipv6', u'dst_ipv6'])
    rx_if = args.get_arg(u'rx_if')
    tx_if = args.get_arg(u'tx_if')
    tx_dst_mac = args.get_arg(u'tx_dst_mac')
    tx_src_ipv4 = args.get_arg(u'tx_src_ipv4')
    tx_dst_ipv4 = args.get_arg(u'tx_dst_ipv4')
    tx_icmp_id = int(args.get_arg(u'tx_icmp_id'))
    rx_dst_mac = args.get_arg(u'rx_dst_mac')
    rx_src_mac = args.get_arg(u'rx_src_mac')
    rx_src_ipv6 = args.get_arg(u'src_ipv6')
    rx_dst_ipv6 = args.get_arg(u'dst_ipv6')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    for icmp_type in (u'echo-request', u'echo-reply'):
        print (f'\nChecking ICMP type: {icmp_type}')

        # Create ICMP request
        tx_pkt = (Ether(dst=tx_dst_mac) /
                  IP(src=tx_src_ipv4, dst=tx_dst_ipv4) /
                  ICMP(type=icmp_type, id=tx_icmp_id))

        txq.send(tx_pkt)
        sent_packets.append(tx_pkt)

        for _ in range(5):
            pkt = rxq.recv(2)
            if _is_ipv4_in_ipv6(pkt):
                ether = pkt
                break
        else:
            raise RuntimeError(f'IPv4 in IPv6 Rx error.')

        # check ethernet
        if ether.dst != rx_dst_mac:
            raise RuntimeError(f'Destination MAC error '
                               f'{ether.dst} != {rx_dst_mac}.')
        print (f'Destination MAC: OK.')

        if ether.src != rx_src_mac:
            raise RuntimeError(f'Source MAC error {ether.src} != {rx_src_mac}.')
        print (f'Source MAC: OK.')

        ipv6 = ether.payload

        # check ipv6
        if ipv6.dst != rx_dst_ipv6:
            raise RuntimeError(f'Destination IP error '
                               f'{ipv6.dst} != {rx_dst_ipv6}.')
        print (f'Destination IPv6: OK.')

        if ipv6.src != rx_src_ipv6:
            raise RuntimeError(f'Source IP error {ipv6.src} != {rx_src_ipv6}.')
        print (f'Source IPv6: OK.')
  
        ipv4 = ipv6.payload

        # check ipv4
        if ipv4.dst != tx_dst_ipv4:
            raise RuntimeError(f'Destination IP error '
                               f'{ipv4.dst} != {tx_dst_ipv4}.')
        print (f'Destination IPv4: OK.')

        if ipv4.src != tx_src_ipv4:
            raise RuntimeError(f'Source IP error {ipv4.src} != {tx_src_ipv4}.')
        print (f'Source IPv4: OK.')

        # check icmp echo request
        if ipv4.proto != 1:  # ICMP
            raise RuntimeError(f'IP protocol error {ipv4.proto} != ICMP.')
        print (f'IPv4 protocol: OK.')

        icmp = ipv4.payload

        # check icmp
        if icmptypes[icmp.type] != icmp_type:
            raise RuntimeError(f'ICMP type error {icmp.type} != echo request.')
        print (f'ICMP type: OK.')

        if icmp.id != tx_icmp_id:
            raise RuntimeError(f'ICMP ID error {icmp.id} != {tx_icmp_id}.')
        print (f'ICMP ID: OK.')

    sys.exit(0)

if __name__ == "__main__":
    main()
