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

"""Traffic script for IPv6 sweep ping."""

import logging
import os
import sys

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue, \
    checksum_equal
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from scapy.layers.inet6 import IPv6, ICMPv6ND_NA, ICMPv6NDOptDstLLAddr
from scapy.layers.inet6 import ICMPv6EchoRequest, ICMPv6EchoReply
from scapy.all import Ether


def main():
    # start_size - start size of the ICMPv6 echo data
    # end_size - end size of the ICMPv6 echo data
    # step - increment step
    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip',
                             'start_size', 'end_size', 'step'])

    rxq = RxQueue(args.get_arg('rx_if'))
    txq = TxQueue(args.get_arg('tx_if'))

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    start_size = int(args.get_arg('start_size'))
    end_size = int(args.get_arg('end_size'))
    step = int(args.get_arg('step'))
    echo_id = 0xa
    # generate some random data buffer
    data = bytearray(os.urandom(end_size))

    # send ICMPv6 neighbor advertisement message
    sent_packets = []
    pkt_send = (Ether(src=src_mac, dst=dst_mac) /
                IPv6(src=src_ip, dst=dst_ip) /
                ICMPv6ND_NA(tgt=src_ip, R=0) /
                ICMPv6NDOptDstLLAddr(lladdr=src_mac))
    sent_packets.append(pkt_send)
    txq.send(pkt_send)

    # send ICMPv6 echo request with incremented data length and receive ICMPv6
    # echo reply
    for echo_seq in range(start_size, end_size + 1, step):
        pkt_send = (Ether(src=src_mac, dst=dst_mac) /
                    IPv6(src=src_ip, dst=dst_ip) /
                    ICMPv6EchoRequest(id=echo_id, seq=echo_seq,
                                      data=data[0:echo_seq]))
        sent_packets.append(pkt_send)
        txq.send(pkt_send)

        ether = rxq.recv(ignore=sent_packets)
        if ether is None:
            raise RuntimeError(
                'ICMPv6 echo reply seq {0} Rx timeout'.format(echo_seq))

        if not ether.haslayer(IPv6):
            raise RuntimeError(
                'Unexpected packet with no IPv6 received {0}'.format(
                    ether.__repr__()))

        ipv6 = ether['IPv6']

        if not ipv6.haslayer(ICMPv6EchoReply):
            raise RuntimeError(
                'Unexpected packet with no IPv6 ICMP received {0}'.format(
                    ipv6.__repr__()))

        icmpv6 = ipv6['ICMPv6 Echo Reply']

        if icmpv6.id != echo_id or icmpv6.seq != echo_seq:
            raise RuntimeError(
                'Invalid ICMPv6 echo reply received ID {0} seq {1} should be '
                'ID {2} seq {3}, {0}'.format(icmpv6.id, icmpv6.seq, echo_id,
                                             echo_seq))

        cksum = icmpv6.cksum
        del icmpv6.cksum
        tmp = ICMPv6EchoReply(str(icmpv6))
        if not checksum_equal(tmp.cksum, cksum):
            raise RuntimeError(
                'Invalid checksum {0} should be {1}'.format(cksum, tmp.cksum))

        sent_packets.remove(pkt_send)

    sys.exit(0)


if __name__ == "__main__":
    main()
