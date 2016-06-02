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

"""Traffic script that sends an IP ICMPv4."""

import sys

from scapy.layers.inet import ICMP, IP
from scapy.all import Ether

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def is_icmp_reply(pkt):
    """Return True if pkt is echo reply, else return False. If exception occurs
    return False."""
    try:
        if pkt['IP']['ICMP'].type == 0:  # 0 - echo-reply
            return True
        else:
            return False
    except:
        return False


def address_check(request, reply):
    """Compare request packet source address with reply destination address
    and vice versa. If exception occurs return False."""
    try:
        return reply['IP'].src == request['IP'].dst \
               and reply['IP'].dst == request['IP'].src
    except:
        return False


def main():
    """Send ICMP echo request and wait for ICMP echo reply. It ignores all other
    packets."""
    args = TrafficScriptArg(['dst_mac', 'src_mac', 'dst_ip', 'src_ip',
                             'timeout'])

    dst_mac = args.get_arg('dst_mac')
    src_mac = args.get_arg('src_mac')
    dst_ip = args.get_arg('dst_ip')
    src_ip = args.get_arg('src_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    timeout = int(args.get_arg('timeout'))
    wait_step = 1

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    # Create empty ip ICMP packet
    icmp_request = (Ether(src=src_mac, dst=dst_mac) /
                    IP(src=src_ip, dst=dst_ip) /
                    ICMP())
    # Send created packet on the interface
    sent_packets.append(icmp_request)
    txq.send(icmp_request)

    for _ in range(1000):
        icmp_reply = rxq.recv(wait_step)
        if icmp_reply is None:
            timeout -= wait_step
            if timeout < 0:
                raise RuntimeError("ICMP echo Rx timeout")
        elif is_icmp_reply(icmp_reply):
            if address_check(icmp_request, icmp_reply):
                break
    else:
        raise RuntimeError("Max packet count limit reached")

    print "ICMP echo reply received."

    sys.exit(0)

if __name__ == "__main__":
    main()
