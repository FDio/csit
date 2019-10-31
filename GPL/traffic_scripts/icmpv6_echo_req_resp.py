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

"""Send ICMPv6 echo request from one TG port to DUT port or to another TG port
   through DUT node(s) and send reply back. Also verify hop limit processing."""

import sys
import logging

# pylint: disable=no-name-in-module
# pylint: disable=import-error
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.layers.inet6 import IPv6, ICMPv6ND_NA, ICMPv6ND_NS
from scapy.layers.inet6 import ICMPv6NDOptDstLLAddr
from scapy.layers.inet6 import ICMPv6EchoRequest, ICMPv6EchoReply
from scapy.all import Ether

from .PacketVerifier import RxQueue, TxQueue, checksum_equal
from .TrafficScriptArg import TrafficScriptArg


def main():
    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_nh_mac', 'dst_nh_mac',
                             'src_ip', 'dst_ip', 'h_num'], ['is_dst_tg'])

    src_rxq = RxQueue(args.get_arg('tx_if'))
    src_txq = TxQueue(args.get_arg('tx_if'))

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_nh_mac = args.get_arg('src_nh_mac')
    dst_nh_mac = args.get_arg('dst_nh_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    hop_num = int(args.get_arg('h_num'))

    is_dst_tg = True if args.get_arg('is_dst_tg') in ['True', ''] else False
    dst_rxq = RxQueue(args.get_arg('rx_if')) if is_dst_tg else None
    dst_txq = TxQueue(args.get_arg('rx_if')) if is_dst_tg else None

    hop_limit = 64
    echo_id = 0xa
    echo_seq = 0x1

    src_sent_packets = []
    dst_sent_packets = []

    # send ICMPv6 neighbor advertisement message
    pkt_send = (Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff') /
                IPv6(src=src_ip, dst='ff02::1:ff00:2') /
                ICMPv6ND_NA(tgt=src_ip, R=0) /
                ICMPv6NDOptDstLLAddr(lladdr=src_mac))
    src_sent_packets.append(pkt_send)
    src_txq.send(pkt_send)

    if is_dst_tg:
        # send ICMPv6 neighbor advertisement message
        pkt_send = (Ether(src=dst_mac, dst='ff:ff:ff:ff:ff:ff') /
                    IPv6(src=dst_ip, dst='ff02::1:ff00:2') /
                    ICMPv6ND_NA(tgt=dst_ip, R=0) /
                    ICMPv6NDOptDstLLAddr(lladdr=dst_mac))
        dst_sent_packets.append(pkt_send)
        dst_txq.send(pkt_send)

    # send ICMPv6 echo request from first TG interface
    pkt_send = (Ether(src=src_mac, dst=src_nh_mac) /
                IPv6(src=src_ip, dst=dst_ip, hlim=hop_limit) /
                ICMPv6EchoRequest(id=echo_id, seq=echo_seq))
    src_sent_packets.append(pkt_send)
    src_txq.send(pkt_send)

    if is_dst_tg:
        # receive ICMPv6 echo request on second TG interface
        while True:
            ether = dst_rxq.recv(2, dst_sent_packets)
            if ether is None:
                raise RuntimeError('ICMPv6 echo reply Rx timeout')

            if ether.haslayer(ICMPv6ND_NS):
                # read another packet in the queue if the current one is
                # ICMPv6ND_NS
                continue
            else:
                # otherwise process the current packet
                break

        if not ether.haslayer(IPv6):
            raise RuntimeError('Unexpected packet with no IPv6 received: {0}'.
                               format(ether.__repr__()))

        ipv6 = ether[IPv6]

        # verify hop limit processing
        if ipv6.hlim != (hop_limit - hop_num):
            raise RuntimeError('Invalid hop limit {0} should be {1}'.
                               format(ipv6.hlim, hop_limit - hop_num))

        if not ipv6.haslayer(ICMPv6EchoRequest):
            raise RuntimeError('Unexpected packet with no IPv6 ICMP received '
                               '{0}'.format(ipv6.__repr__()))

        icmpv6 = ipv6[ICMPv6EchoRequest]

        # check identifier and sequence number
        if icmpv6.id != echo_id or icmpv6.seq != echo_seq:
            raise RuntimeError('Invalid ICMPv6 echo reply received ID {0} '
                               'seq {1} should be ID {2} seq {3}'.
                               format(icmpv6.id, icmpv6.seq, echo_id, echo_seq))

        # verify checksum
        cksum = icmpv6.cksum
        del icmpv6.cksum
        tmp = ICMPv6EchoRequest(str(icmpv6))
        if not checksum_equal(tmp.cksum, cksum):
            raise RuntimeError('Invalid checksum {0} should be {1}'.
                               format(cksum, tmp.cksum))

        # send ICMPv6 echo reply from second TG interface
        pkt_send = (Ether(src=dst_mac, dst=dst_nh_mac) /
                    IPv6(src=dst_ip, dst=src_ip, hlim=(ipv6.hlim - 1)) /
                    ICMPv6EchoReply(id=echo_id, seq=echo_seq))
        dst_sent_packets.append(pkt_send)
        dst_txq.send(pkt_send)

    # receive ICMPv6 echo reply on first TG interface
    while True:
        ether = src_rxq.recv(2, src_sent_packets)
        if ether is None:
            raise RuntimeError('ICMPv6 echo reply Rx timeout')

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if not ether.haslayer(IPv6):
        raise RuntimeError('Unexpected packet with no IPv6 layer received {0}'.
                           format(ether.__repr__()))

    ipv6 = ether[IPv6]

    # verify hop limit processing; destination node decrements hlim by one in
    # outgoing ICMPv6 Echo Reply
    directions = 2 if is_dst_tg else 1
    hop_limit_reply = hop_limit - directions * hop_num - 1
    if ipv6.hlim != hop_limit_reply:
        raise RuntimeError('Invalid hop limit {0} should be {1}'.
                           format(ipv6.hlim, hop_limit_reply))

    if not ipv6.haslayer(ICMPv6EchoReply):
        raise RuntimeError('Unexpected packet with no IPv6 ICMP received {0}'.
                           format(ipv6.__repr__()))

    icmpv6 = ipv6[ICMPv6EchoReply]

    # check identifier and sequence number
    if icmpv6.id != echo_id or icmpv6.seq != echo_seq:
        raise RuntimeError('Invalid ICMPv6 echo reply received ID {0} '
                           'seq {1} should be ID {2} seq {3}'.
                           format(icmpv6.id, icmpv6.seq, echo_id, echo_seq))

    # verify checksum
    cksum = icmpv6.cksum
    del icmpv6.cksum
    tmp = ICMPv6EchoReply(str(icmpv6))
    if not checksum_equal(tmp.cksum, cksum):
        raise RuntimeError('Invalid checksum {0} should be {1}'.
                           format(cksum, tmp.cksum))

    sys.exit(0)


if __name__ == "__main__":
    main()
