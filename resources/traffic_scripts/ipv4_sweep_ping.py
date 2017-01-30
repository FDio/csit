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

"""Traffic script for IPv4 sweep ping."""

import logging
import os
import sys

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue, \
    create_gratuitous_arp_request, checksum_equal
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from scapy.layers.inet import IP, ICMP
from scapy.all import Ether, Raw


def main():
    # start_size - start size of the ICMPv4 echo data
    # end_size - end size of the ICMPv4 echo data
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

    sent_packets = []
    pkt_send = create_gratuitous_arp_request(src_mac, src_ip)
    sent_packets.append(pkt_send)
    txq.send(pkt_send)

    # send ICMP echo request with incremented data length and receive ICMP
    # echo reply
    for echo_seq in range(start_size, end_size + 1, step):
        pkt_send = (Ether(src=src_mac, dst=dst_mac) /
                    IP(src=src_ip, dst=dst_ip) /
                    ICMP(id=echo_id, seq=echo_seq) /
                    Raw(load=data[0:echo_seq]))
        sent_packets.append(pkt_send)
        txq.send(pkt_send)

        ether = rxq.recv(ignore=sent_packets)
        if ether is None:
            raise RuntimeError(
                'ICMP echo reply seq {0} Rx timeout'.format(echo_seq))

        if not ether.haslayer(IP):
            raise RuntimeError(
                'Unexpected packet with no IPv4 received {0}'.format(
                    ether.__repr__()))

        ipv4 = ether['IP']

        if not ipv4.haslayer(ICMP):
            raise RuntimeError(
                'Unexpected packet with no ICMP received {0}'.format(
                    ipv4.__repr__()))

        icmpv4 = ipv4['ICMP']

        if icmpv4.id != echo_id or icmpv4.seq != echo_seq:
            raise RuntimeError(
                'Invalid ICMP echo reply received ID {0} seq {1} should be '
                'ID {2} seq {3}, {0}'.format(icmpv4.id, icmpv4.seq, echo_id,
                                             echo_seq))

        chksum = icmpv4.chksum
        del icmpv4.chksum
        tmp = ICMP(str(icmpv4))
        if not checksum_equal(tmp.chksum, chksum):
            raise RuntimeError(
                'Invalid checksum {0} should be {1}'.format(chksum, tmp.chksum))

        if 'Raw' in icmpv4:
            load = icmpv4['Raw'].load
        else:
            load = ""
        if load != data[0:echo_seq]:
            raise RuntimeError(
                'Received ICMP payload does not match sent payload')

        sent_packets.remove(pkt_send)

    sys.exit(0)


if __name__ == "__main__":
    main()
