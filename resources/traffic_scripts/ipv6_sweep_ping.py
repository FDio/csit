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

# pylint: disable=no-name-in-module
# pylint: disable=import-error
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.layers.l2 import Ether
from scapy.layers.inet6 import IPv6, ICMPv6ND_NA, ICMPv6ND_NS
from scapy.layers.inet6 import ICMPv6NDOptDstLLAddr
from scapy.layers.inet6 import ICMPv6EchoRequest, ICMPv6EchoReply

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.PacketVerifier import checksum_equal
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    # start_size - start size of the ICMPv6 echo data
    # end_size - end size of the ICMPv6 echo data
    # step - increment step
    args = TrafficScriptArg([u'src_mac', u'dst_mac', u'src_ip', u'dst_ip',
                             u'start_size', u'end_size', u'step'])

    rxq = RxQueue(args.get_arg(u'rx_if'))
    txq = TxQueue(args.get_arg(u'tx_if'))

    src_mac = args.get_arg(u'src_mac')
    dst_mac = args.get_arg(u'dst_mac')
    src_ip = args.get_arg(u'src_ip')
    dst_ip = args.get_arg(u'dst_ip')
    start_size = int(args.get_arg(u'start_size'))
    end_size = int(args.get_arg(u'end_size'))
    step = int(args.get_arg(u'step'))
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

        while True:
            ether = rxq.recv(ignore=sent_packets)
            if ether is None:
                raise RuntimeError(f'ICMPv6 echo reply seq {echo_seq} u'
                                   f'Rx timeout')

            if ether.haslayer(ICMPv6ND_NS):
                # read another packet in the queue in case of ICMPv6ND_NS packet
                continue
            else:
                # otherwise process the current packet
                break

        if not ether.haslayer(IPv6):
            raise RuntimeError(f'Unexpected packet with no IPv6 layer u'
                               f'received: {ether.__repr__()}')

        ipv6 = ether[IPv6]

        if not ipv6.haslayer(ICMPv6EchoReply):
            raise RuntimeError(f'Unexpected packet with no ICMPv6 echo reply u'
                               f'layer received: {ipv6.__repr__()}')

        icmpv6 = ipv6[ICMPv6EchoReply]

        if icmpv6.id != echo_id or icmpv6.seq != echo_seq:
            raise RuntimeError(f'ICMPv6 echo reply with invalid '
                               f'data received: u '
                               f'ID {icmpv6.id} seq {icmpv6.seq} should be ID '
                               f'{echo_id} seq {echo_seq}, {icmpv6.id}')

        cksum = icmpv6.cksum
        del icmpv6.cksum
        tmp = ICMPv6EchoReply(str(icmpv6))
        if not checksum_equal(tmp.cksum, cksum):
            raise RuntimeError(f'Invalid checksum: {cksum} '
                               f'should be {tmp.cksum}')

        sent_packets.remove(pkt_send)

    sys.exit(0)


if __name__ == "__main__":
    main()
