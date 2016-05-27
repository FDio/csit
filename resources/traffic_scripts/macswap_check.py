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

"""Macswap test."""

from scapy.all import Ether, IP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg

def check_macswap(pkt_send, pkt_recv):
    """Compare MAC addresses of sent and received packet.

    :param pkt_send: Sent packet.
    :param pkt_recv: Received packet.
    :type pkt_send: Ether
    :type pkt_recv: Ether
    """
    print "Comparing following packets:"
    pkt_send.show2()
    pkt_recv.show2()

    if pkt_send.dst != pkt_recv.src or pkt_send.src != pkt_recv.dst:
        raise RuntimeError("MAC addresses hasn't been swapped.")


def main():
    """Main function."""
    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip'])

    rxq = RxQueue(args.get_arg('rx_if'))
    txq = TxQueue(args.get_arg('tx_if'))

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')

    pkt_send = (Ether(src=src_mac, dst=dst_mac) /
                    IP(src=src_ip, dst=dst_ip, proto=61))

    sent_packets = []
    sent_packets.append(pkt_send)
    txq.send(pkt_send)

    pkt_recv = rxq.recv(ignore=sent_packets)

    if pkt_recv is None:
        raise RuntimeError('Timeout waiting for packet')

    check_macswap(pkt_send, pkt_recv)

if __name__ == "__main__":
    main()
