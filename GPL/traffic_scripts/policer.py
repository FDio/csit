#!/usr/bin/env python3

# Copyright (c) 2021 Cisco and/or its affiliates.
#
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
#
# Licensed under the Apache License 2.0 or
# GNU General Public License v2.0 or later;  you may not use this file
# except in compliance with one of these Licenses. You
# may obtain a copy of the Licenses at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
#
# Note: If this file is linked with Scapy, which is GPLv2+, your use of it
# must be under GPLv2+.  If at any point in the future it is no longer linked
# with Scapy (or other GPLv2+ licensed software), you are free to choose
# Apache 2.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Traffic script for IPsec verification."""

import sys
import logging

from ipaddress import ip_address
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.packet import Raw

from .TrafficScriptArg import TrafficScriptArg
from .PacketVerifier import RxQueue, TxQueue


def check_ipv4(pkt_recv, dscp):
    """Check received IPv4 IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param dscp: DSCP value to check.
    :type pkt_recv: scapy.Ether
    :type dscp: int
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(IP):
        raise RuntimeError(f"Not an IPv4 packet received: {pkt_recv!r}")

    rx_dscp = pkt_recv[IP].tos >> 2
    if rx_dscp != dscp:
        raise RuntimeError(f"Invalid DSCP {rx_dscp} should be {dscp}")

    if not pkt_recv.haslayer(TCP):
        raise RuntimeError(f"Not a TCP packet received: {pkt_recv!r}")


def check_ipv6(pkt_recv, dscp):
    """Check received IPv6 IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param dscp: DSCP value to check.
    :type pkt_recv: scapy.Ether
    :type dscp: int
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(IPv6):
        raise RuntimeError(f"Not an IPv6 packet received: {pkt_recv!r}")

    rx_dscp = pkt_recv[IPv6].tc >> 2
    if rx_dscp != dscp:
        raise RuntimeError(f"Invalid DSCP {rx_dscp} should be {dscp}")

    if not pkt_recv.haslayer(TCP):
        raise RuntimeError(f"Not a TCP packet received: {pkt_recv!r}")


# TODO: Pylint says too-many-locals and too-many-statements. Refactor!
def main():
    """Send and receive TCP packet."""
    args = TrafficScriptArg(
        [u"src_mac", u"dst_mac", u"src_ip", u"dst_ip", u"dscp"]
    )

    rxq = RxQueue(args.get_arg(u"rx_if"))
    txq = TxQueue(args.get_arg(u"tx_if"))

    src_mac = args.get_arg(u"src_mac")
    dst_mac = args.get_arg(u"dst_mac")
    src_ip = args.get_arg(u"src_ip")
    dst_ip = args.get_arg(u"dst_ip")
    dscp = int(args.get_arg(u"dscp"))

    ip_layer = IPv6 if ip_address(src_ip).version == 6 else IP

    sent_packets = list()
    pkt_send = (Ether(src=src_mac, dst=dst_mac) /
                ip_layer(src=src_ip, dst=dst_ip) /
                TCP())

    pkt_send /= Raw()
    sent_packets.append(pkt_send)
    txq.send(pkt_send)

    while True:
        pkt_recv = rxq.recv(2, sent_packets)
        if pkt_recv is None:
            raise RuntimeError(u"ICMPv6 echo reply Rx timeout")

        if pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if pkt_recv is None:
        raise RuntimeError(u"Rx timeout")

    if ip_layer == IP:
        check_ipv4(pkt_recv, dscp)
    else:
        check_ipv6(pkt_recv, dscp)

    sys.exit(0)


if __name__ == u"__main__":
    main()
