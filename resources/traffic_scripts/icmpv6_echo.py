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

"""Traffic script for ICMPv6 echo test."""

import sys
import logging

# pylint: disable=no-name-in-module
# pylint: disable=import-error
logging.getLogger(u"scapy.runtime").setLevel(logging.ERROR)

from scapy.layers.l2 import Ether
from scapy.layers.inet6 import IPv6, ICMPv6ND_NA, ICMPv6ND_NS
from scapy.layers.inet6 import ICMPv6NDOptDstLLAddr
from scapy.layers.inet6 import ICMPv6EchoRequest, ICMPv6EchoReply

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
    echo_id = 0xa
    echo_seq = 0x1

    sent_packets = []

    # send ICMPv6 neighbor advertisement message
    pkt_send = (Ether(src=src_mac, dst=u'ff:ff:ff:ff:ff:ff') /
                IPv6(src=src_ip, dst=u'ff02::1:ff00:2') /
                ICMPv6ND_NA(tgt=src_ip, R=0) /
                ICMPv6NDOptDstLLAddr(lladdr=src_mac))
    sent_packets.append(pkt_send)
    txq.send(pkt_send)

    # send ICMPv6 echo request
    pkt_send = (Ether(src=src_mac, dst=dst_mac) /
                IPv6(src=src_ip, dst=dst_ip) /
                ICMPv6EchoRequest(id=echo_id, seq=echo_seq))
    sent_packets.append(pkt_send)
    txq.send(pkt_send)

    # receive ICMPv6 echo reply
    while True:
        ether = rxq.recv(2, sent_packets)
        if ether is None:
            raise RuntimeError(f'ICMPv6 echo reply Rx timeout')

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if not ether.haslayer(IPv6):
        raise RuntimeError(f'Unexpected packet with no IPv6 received'
                           f' {ether.__repr__()}')

    ipv6 = ether[IPv6]

    if not ipv6.haslayer(ICMPv6EchoReply):
        raise RuntimeError(f'Unexpected packet with no ICMPv6 echo reply '
                           f'received {ipv6.__repr__()}')

    icmpv6 = ipv6[ICMPv6EchoReply]

    # check identifier and sequence number
    if icmpv6.id != echo_id or icmpv6.seq != echo_seq:
        raise RuntimeError(f'Invalid ICMPv6 echo reply'
                           f' received ID {icmpv6.id} seq {icmpv6.seq} '
                           f'should be ID {echo_id} seq {echo_seq}')

    # verify checksum
    cksum = icmpv6.cksum
    del icmpv6.cksum
    tmp = ICMPv6EchoReply(str(icmpv6))
    if not checksum_equal(tmp.cksum, cksum):
        raise RuntimeError(f'Invalid checksum {cksum} should be {tmp.cksum}')

    sys.exit(0)


if __name__ == "__main__":
    main()
