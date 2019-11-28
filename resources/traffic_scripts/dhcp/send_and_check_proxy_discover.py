#!/usr/bin/env python
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the u"License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an u"AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Traffic script that sends DHCP DISCOVER packet
 and check if is received on interface."""

import sys

from scapy.all import Ether
from scapy.layers.inet import IP, UDP
from scapy.layers.inet import UDP_SERVICES
from scapy.layers.dhcp import DHCP, BOOTP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def is_discover(pkt):
    u"""If DHCP message type option is set to dhcp discover return True,
    else return False. False is returned also if exception occurs."""
    dhcp_discover = 1
    try:
        dhcp_options = pkt[u'BOOTP'][u'DHCP options'].options
        message_type = filter(lambda x: x[0] == u'message-type',
                              dhcp_options)
        message_type = message_type[0][1]
        return message_type == dhcp_discover
    except:
        return False


def main():
    u"""Send DHCP DISCOVER packet."""

    args = TrafficScriptArg([u'tx_src_ip', u'tx_dst_ip'])

    tx_if = args.get_arg(u'tx_if')
    rx_if = args.get_arg(u'rx_if')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    tx_src_ip = args.get_arg(u'tx_src_ip')
    tx_dst_ip = args.get_arg(u'tx_dst_ip')

    sent_packets = []

    dhcp_discover = Ether(dst=u"ff:ff:ff:ff:ff:ff") / \
                    IP(src=tx_src_ip, dst=tx_dst_ip) / \
                    UDP(sport=UDP_SERVICES.bootpc, dport=UDP_SERVICES.bootps) / \
                    BOOTP(op=1,) / \
                    DHCP(options=[(u"message-type", u"discover"),
                                  u"end"])

    sent_packets.append(dhcp_discover)
    txq.send(dhcp_discover)

    for _ in range(10):
        dhcp_discover = rxq.recv(2)
        if is_discover(dhcp_discover):
            break
    else:
        raise RuntimeError(u"DHCP DISCOVER Rx timeout")

    sys.exit(0)

if __name__ == "__main__":
    main()
