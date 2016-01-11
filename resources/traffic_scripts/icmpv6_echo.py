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
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from scapy.layers.inet6 import IPv6, ICMPv6ND_NA, ICMPv6NDOptDstLLAddr
from scapy.layers.inet6 import ICMPv6EchoRequest, ICMPv6EchoReply
from scapy.all import Ether


def main():
    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip'])

    rxq = RxQueue(args.get_arg('rx_if'))
    txq = TxQueue(args.get_arg('tx_if'))

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    echo_id = 0xa
    echo_seq = 0x1

    sent_packets = []

    # send ICMPv6 neighbor advertisement message
    pkt_send = (Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff') /
                        IPv6(src=src_ip, dst='ff02::1:ff00:2') /
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
    ether = rxq.recv(2, sent_packets)
    if ether is None:
        rxq._proc.terminate()
        raise RuntimeError('ICMPv6 echo reply Rx timeout')

    if not ether.haslayer(IPv6):
        rxq._proc.terminate()
        raise RuntimeError('Unexpected packet with no IPv6 received {0}'.format(
            ether.__repr__()))

    ipv6 = ether['IPv6']

    if not ipv6.haslayer(ICMPv6EchoReply):
        rxq._proc.terminate()
        raise RuntimeError(
            'Unexpected packet with no IPv6 ICMP received {0}'.format(
                ipv6.__repr__()))

    icmpv6 = ipv6['ICMPv6 Echo Reply']

    # check identifier and sequence number
    if icmpv6.id != echo_id or icmpv6.seq != echo_seq:
        rxq._proc.terminate()
        raise RuntimeError(
            'Invalid ICMPv6 echo reply received ID {0} seq {1} should be ' +
            'ID {2} seq {3}'.format(icmpv6.id, icmpv6.seq, echo_id, echo_seq))

    # verify checksum
    cksum = icmpv6.cksum
    del icmpv6.cksum
    tmp = ICMPv6EchoReply(str(icmpv6))
    if tmp.cksum != cksum:
        rxq._proc.terminate()
        raise RuntimeError(
            'Invalid checksum {0} should be {1}'.format(cksum, tmp.cksum))

    rxq._proc.terminate()
    sys.exit(0)

if __name__ == "__main__":
    main()
