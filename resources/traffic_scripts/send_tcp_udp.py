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

"""Traffic script that sends an TCP or UDP packet
from one interface to the other.
"""

import sys

from scapy.layers.inet import IP, UDP, TCP
from scapy.all import Ether
from robot.api import logger

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    """Send TCP or UDP packet from one traffic generator interface to the other.
    """
    args = TrafficScriptArg(
        ['tx_mac', 'rx_mac', 'src_ip', 'dst_ip', 'protocol',
         'source_port', 'destination_port'])

    src_mac = args.get_arg('tx_mac')
    dst_mac = args.get_arg('rx_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')

    protocol = args.get_arg('protocol')
    source_port = args.get_arg('source_port')
    destination_port = args.get_arg('destination_port')

    if protocol.upper() == 'TCP':
        protocol = TCP
    elif protocol.upper() == 'UDP':
        protocol = UDP
    else:
        raise ValueError("Invalid type of protocol!")

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
               IP(src=src_ip, dst=dst_ip) /
               protocol(sport=int(source_port), dport=int(destination_port)))

    txq.send(pkt_raw)
    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError("TCP/UDP Rx timeout")

    if ether['TCP'] is not None:
        logger.trace("TCP matched")

    elif ether['UDP'] is not None:
        logger.trace("UDP matched")
    else:
        raise RuntimeError("Not an TCP or UDP packet received {0}"
                           .format(ether.__repr__()))

    sys.exit(0)


if __name__ == "__main__":
    main()
