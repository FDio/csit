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

"""Traffic script that sends DHCP DISCOVER packet
 and check if is received on interface."""

import sys

from scapy.all import Ether
from scapy.layers.inet import IP, UDP
from scapy.layers.inet import UDP_SERVICES
from scapy.layers.dhcp import DHCP, BOOTP

from ..PacketVerifier import RxQueue, TxQueue
from ..TrafficScriptArg import TrafficScriptArg


def is_discover(pkt):
    """If DHCP message type option is set to dhcp discover return True,
    else return False. False is returned also if exception occurs."""
    dhcp_discover = 1
    try:
        dhcp_options = pkt['BOOTP']['DHCP options'].options
        message_type = filter(lambda x: x[0] == 'message-type',
                              dhcp_options)
        message_type = message_type[0][1]
        return message_type == dhcp_discover
    except:
        return False


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
                    UDP(sport=UDP_SERVICES.bootpc, dport=UDP_SERVICES.bootps) / \
                    BOOTP(op=1,) / \
                    DHCP(options=[("message-type", "discover"),
                                  "end"])

    sent_packets.append(dhcp_discover)
    txq.send(dhcp_discover)

    for _ in range(10):
        dhcp_discover = rxq.recv(2)
        if is_discover(dhcp_discover):
            break
    else:
        raise RuntimeError("DHCP DISCOVER Rx timeout")

    sys.exit(0)

if __name__ == "__main__":
    main()
