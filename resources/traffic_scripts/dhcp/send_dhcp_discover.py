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

"""Traffic script that sends DHCP DISCOVER packets."""

import sys

from scapy.all import Ether
from scapy.layers.inet import IP, UDP
from scapy.layers.inet import UDP_SERVICES
from scapy.layers.dhcp import DHCP, BOOTP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    """Send DHCP DISCOVER packet."""

    args = TrafficScriptArg(['tx_src_ip', 'tx_dst_ip'])

    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    tx_src_ip = args.get_arg('tx_src_ip')
    tx_dst_ip = args.get_arg('tx_dst_ip')

    sent_packets = []

    dhcp_discover = Ether(dst="ff:ff:ff:ff:ff:ff") / \
                    IP(src=tx_src_ip, dst=tx_dst_ip) / \
                    UDP(sport=68, dport=67) / \
                    BOOTP(op=1,) / \
                    DHCP(options=[("message-type", "discover"),
                                  ])

    sent_packets.append(dhcp_discover)
    txq.send(dhcp_discover)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCP DISCOVER timeout')

    if ether[UDP].dport != UDP_SERVICES.bootps:
        raise RuntimeError("UDP destination port error.")
    print "UDP destination port: OK."

    if ether[UDP].sport != UDP_SERVICES.bootpc:
        raise RuntimeError("UDP source port error.")
    print "UDP source port: OK."

    if ether[DHCP].options[0][1] != 1:  # 1 - DISCOVER message
        raise RuntimeError("DHCP DISCOVER message error.")
    print "DHCP DISCOVER message OK."

    sys.exit(0)

if __name__ == "__main__":
    main()
