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

"""Traffic script for IPv6 Neighbor Solicitation test."""

import sys
import logging

# pylint: disable=no-name-in-module
# pylint: disable=import-error
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.layers.l2 import Ether
from scapy.layers.inet6 import IPv6, ICMPv6ND_NA, ICMPv6ND_NS
from scapy.layers.inet6 import ICMPv6NDOptDstLLAddr, ICMPv6NDOptSrcLLAddr

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.PacketVerifier import checksum_equal
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    args = TrafficScriptArg([u'src_mac', u'dst_mac', u'src_ip', u'dst_ip'])

    rxq = RxQueue(args.get_arg(u'rx_if'))
    txq = TxQueue(args.get_arg(u'tx_if'))

    src_mac = args.get_arg(u'src_mac')
    dst_mac = args.get_arg(u'dst_mac')
    src_ip = args.get_arg(u'src_ip')
    dst_ip = args.get_arg(u'dst_ip')

    sent_packets = []

    # send ICMPv6 neighbor solicitation message
    pkt_send = (Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff') /
                IPv6(src=src_ip, dst='ff02::1:ff00:2') /
                ICMPv6ND_NS(tgt=dst_ip) /
                ICMPv6NDOptSrcLLAddr(lladdr=src_mac))
    sent_packets.append(pkt_send)
    txq.send(pkt_send)

    # receive ICMPv6 neighbor advertisement message
    while True:
        ether = rxq.recv(2, sent_packets)
        if ether is None:
            raise RuntimeError(u'ICMPv6 echo reply Rx timeout')

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if ether is None:
        raise RuntimeError(u'ICMPv6 echo reply Rx timeout')

    if not ether.haslayer(IPv6):
        raise RuntimeError(f'Unexpected packet with no IPv6 received '
                           f'{ether.__repr__()}')

    ipv6 = ether[IPv6]

    if not ipv6.haslayer(ICMPv6ND_NA):
        raise RuntimeError(f'Unexpected packet with no ICMPv6 ND-NA received u'
                           f'{ipv6.__repr__()}')

    icmpv6_na = ipv6[ICMPv6ND_NA]

    # verify target address
    if icmpv6_na.tgt != dst_ip:
        raise RuntimeError(f'Invalid target address {icmpv6_na.tgt} '
                           f'should be {dst_ip}')

    if not icmpv6_na.haslayer(ICMPv6NDOptDstLLAddr):
        raise RuntimeError(f'Missing Destination Link-Layer Address option in u'
                           f'ICMPv6 Neighbor Advertisement '
                           f'{icmpv6_na.__repr__()}')

    dst_ll_addr = icmpv6_na[ICMPv6NDOptDstLLAddr]

    # verify destination link-layer address field
    if dst_ll_addr.lladdr != dst_mac:
        raise RuntimeError(f'Invalid lladdr {dst_ll_addr.lladdr} ' 
                           f'should be {dst_mac}')

    # verify checksum
    cksum = icmpv6_na.cksum
    del icmpv6_na.cksum
    tmp = ICMPv6ND_NA(str(icmpv6_na))
    if not checksum_equal(tmp.cksum, cksum):
        raise RuntimeError(f'Invalid checksum {cksum} should be {tmp.cksum}')

    sys.exit(0)


if __name__ == "__main__":
    main()
