#!/usr/bin/env python3

# Copyright (c) 2020 Intel and/or its affiliates.
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
# with Scapy (or other GPLv2+ licensed software), you are free to choose Apache 2.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Traffic script that send flow packet from one interface
to the other.
"""

import sys

from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether
from scapy.packet import Raw
from scapy.volatile import RandIP, RandIP6

from .PacketVerifier import TxQueue
from .TrafficScriptArg import TrafficScriptArg

#from robot.api import logger

def main():
    """Send packet from one traffic generator interface to the other."""

    args = TrafficScriptArg(
        [
            u"tg_if1_mac", u"dut_if1_mac", u"flow_type", u"proto",
            u"src_ip", u"dst_ip", u"src_port", u"dst_port"
        ]
    )
    tx_src_mac = args.get_arg(u"tg_if1_mac")
    tx_dst_mac = args.get_arg(u"dut_if1_mac")
    flow_type = args.get_arg(u"flow_type")
    proto = args.get_arg(u"proto")
    src = args.get_arg(u"src_ip")
    dst = args.get_arg(u"dst_ip")
    sport = int(args.get_arg(u"src_port"))
    dport = int(args.get_arg(u"dst_port"))
    tx_if = args.get_arg(u"tx_if")
    txq = TxQueue(tx_if)
    sent_packets = list()

    if flow_type == u"IP4_N_TUPLE":
        pkt_raw = Ether(src=tx_src_mac, dst=tx_dst_mac, type=0x800)
        pkt_raw /= IP(src=src, dst=dst)
        if proto == u"TCP":
            pkt_raw /= TCP(sport=sport, dport=dport)
        elif proto == u"UDP":
            pkt_raw /= UDP(sport=sport, dport=dport)
        else:
            raise ValueError(u"Proto type error")
    elif flow_type == u"IP6_N_TUPLE":
        pkt_raw = Ether(src=tx_src_mac, dst=tx_dst_mac, type=0x86DD)
        pkt_raw /= IPv6(src=src, dst=dst)
        if proto == u"TCP":
            pkt_raw /= TCP(sport=sport, dport=dport)
        elif proto == u"UDP":
            pkt_raw /= UDP(sport=sport, dport=dport)
        else:
            raise ValueError(u"Proto type error")
    else:
        raise ValueError(u"Flow type error")

    pkt_raw /= Raw(load='X'*100)
    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)
    sys.exit(0)

if __name__ == u"__main__":
    main()
