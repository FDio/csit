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

"""Traffic script that sends an IP ICMPv4 or ICMPv6."""

import sys

from scapy.layers.inet import ICMP, IP
from scapy.layers.inet6 import ICMPv6EchoRequest, ICMPv6EchoReply
from scapy.layers.l2 import Ether
from scapy.packet import Raw

from .PacketVerifier import start_4_queues
from .TrafficScriptArg import TrafficScriptArg
from .ValidIp import valid_ipv4, valid_ipv6


def main():
    """Send ICMP echo request and wait for ICMP echo reply. It ignores all other
    packets."""
    args = TrafficScriptArg(
        [u"dst_mac", u"src_mac", u"dst_ip", u"src_ip", u"timeout"]
    )

    dst_mac = args.get_arg(u"dst_mac")
    src_mac = args.get_arg(u"src_mac")
    dst_ip = args.get_arg(u"dst_ip")
    src_ip = args.get_arg(u"src_ip")
    timeout = int(args.get_arg(u"timeout"))
    wait_step = 1

    txq, _, _, rxq = start_4_queues(args)

    # Create empty ip ICMP packet
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        ip_layer = IP
        icmp_req = ICMP
        icmp_resp = ICMP
        icmp_type = 0  # echo-reply
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        ip_layer = IP
        icmp_req = ICMPv6EchoRequest
        icmp_resp = ICMPv6EchoReply
        icmp_type = 0  # Echo Reply
    else:
        raise ValueError(u"IP not in correct format")

    icmp_request = (
        Ether(src=src_mac, dst=dst_mac) /
        ip_layer(src=src_ip, dst=dst_ip) /
        icmp_req()
    )

    # Send created packet on the interface
    icmp_request /= Raw()
    monotonic_sent = txq.send(icmp_request)

    for _ in range(1000):
        while True:
            icmp_reply = rxq.recv(
                wait_step, do_raise=False, monotonic_sent=monotonic_sent
            )
            if icmp_reply is None:
                timeout -= wait_step
                if timeout < 0:
                    raise RuntimeError(u"ICMP echo Rx timeout")

            break

        if icmp_reply[ip_layer][icmp_resp].type == icmp_type:
            if icmp_reply[ip_layer].src == dst_ip and \
                    icmp_reply[ip_layer].dst == src_ip:
                break
    else:
        raise RuntimeError(u"Max packet count limit reached")

    print(u"ICMP echo reply received.")

    sys.exit(0)


if __name__ == u"__main__":
    main()
