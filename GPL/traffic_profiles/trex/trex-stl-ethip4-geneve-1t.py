# Copyright (c) 2023 Cisco and/or its affiliates.
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

"""Stream profile for T-rex traffic generator.

Stream profile:
 - Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
 - Direction 0 --> 1:
   - Packet: ETH / IP
   - Source IP address range:            10.128.1.0 - 10.128.1.255
   - Destination IP address range:       10.0.1.0 - 10.0.1.255
 - Direction 1 --> 0:
   - Packet: ETH / IP / UDP / GENEVE / ETH / IP
   - Outer Source IP address range:      1.1.1.1
   - Outer Destination IP address range: 1.1.1.2
   - Inner Source IP address range:      10.0.1.0 - 10.0.1.255
   - Inner Destination IP address range: 10.128.1.0 - 10.128.1.255
   - Source UDP port range:              1024 - 1279
   - Destination UDP port range:         6081
"""

from ctypes import c_int
from ipaddress import IPv4Address

from scapy.contrib.geneve import GENEVE
from trex.stl.api import *

from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # Nr. of GENEVE tunnels
        self.n_tunnels = 1
        # VNIs used in GENEVE headers of Direction 1 --> 0.
        self.p2_geneve_start_vni = 1

        # IPs used in packet headers of Direction 0 --> 1.
        self.p1_src_start_ip = "10.128.1.0"
        self.p1_dst_start_ip = "10.0.1.0"

        # IPs used in packet headers of Direction 1 --> 0.
        self.p2_outer_src_ip = "1.1.1.1"
        self.p2_outer_dst_ip = "1.1.1.2"

        self.p2_inner_src_start_ip = "10.0.1.0"
        self.p2_inner_dst_start_ip = "10.128.1.0"

        # MACs used in inner ethernet header of Direction 1 --> 0.
        self.p2_inner_dst_mac = "d0:0b:ee:d0:00:00"

        # UDP ports used in packet headers of Direction 1 --> 0.
        self.p2_udp_sport_start = 1024
        self.p2_udp_dport = 6081

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IP | UDP |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """
        p1_src_start_ip_int = int(IPv4Address(self.p1_src_start_ip))
        p1_dst_start_ip_int = int(IPv4Address(self.p1_dst_start_ip))
        p2_inner_src_start_ip_int = int(IPv4Address(self.p2_inner_src_start_ip))
        p2_inner_dst_start_ip_int = int(IPv4Address(self.p2_inner_dst_start_ip))

        # Direction 0 --> 1
        base_pkt_a = Ether() / IP(
            src=self.p1_src_start_ip, dst=self.p1_dst_start_ip, proto=61
        )
        # Direction 1 --> 0
        base_pkt_b = (
            Ether()
            / IP(src=self.p2_outer_src_ip, dst=self.p2_outer_dst_ip, proto=17)
            / UDP(sport=self.p2_udp_sport_start, dport=self.p2_udp_dport)
            / GENEVE(vni=self.p2_geneve_start_vni)
            / Ether(dst=self.p2_inner_dst_mac)
            / IP(
                src=self.p2_inner_src_start_ip,
                dst=self.p2_inner_dst_start_ip,
                proto=61,
            )
        )
        base_pkt_b /= Raw(load=self._gen_payload(110 - len(base_pkt_b)))
        # Direction 0 --> 1
        vm1 = STLScVmRaw(
            [
                STLVmFlowVar(
                    name="ip_src",
                    min_value=p1_src_start_ip_int,
                    max_value=p1_src_start_ip_int + self.n_tunnels * 256 - 1,
                    size=4,
                    op="inc",
                ),
                STLVmWrFlowVar(fv_name="ip_src", pkt_offset="IP.src"),
                STLVmFlowVar(
                    name="ip_dst",
                    min_value=p1_dst_start_ip_int,
                    max_value=p1_dst_start_ip_int + self.n_tunnels * 256 - 1,
                    size=4,
                    op="inc",
                ),
                STLVmWrFlowVar(fv_name="ip_dst", pkt_offset="IP.dst"),
                STLVmFixIpv4(offset="IP"),
            ]
        )
        # Direction 1 --> 0
        vm2 = STLScVmRaw(
            [
                STLVmFlowVar(
                    name="ip",
                    min_value=0,
                    max_value=self.n_tunnels * 256 - 1,
                    size=4,
                    op="inc",
                ),
                STLVmWrMaskFlowVar(
                    fv_name="ip",
                    pkt_cast_size=4,
                    mask=0xFFFFFFFF,
                    add_value=p2_inner_src_start_ip_int,
                    pkt_offset="IP:1.src",
                ),
                STLVmWrMaskFlowVar(
                    fv_name="ip",
                    pkt_cast_size=4,
                    mask=0xFFFFFFFF,
                    add_value=p2_inner_dst_start_ip_int,
                    pkt_offset="IP:1.dst",
                ),
                STLVmWrMaskFlowVar(
                    fv_name="ip",
                    pkt_cast_size=2,
                    mask=0xFFFF,
                    add_value=self.p2_udp_sport_start,
                    pkt_offset="UDP.sport",
                ),
                STLVmWrMaskFlowVar(
                    fv_name="ip",
                    pkt_cast_size=4,
                    mask=0xFFFFFF00,
                    add_value=(self.p2_geneve_start_vni << 8),
                    pkt_offset="GENEVE.vni",
                ),
                STLVmWrMaskFlowVar(
                    fv_name="ip",
                    pkt_cast_size=4,
                    mask=0xFFFFFF,
                    shift=-8,
                    offset_fixup=2,
                    add_value=c_int(
                        int(self.p2_inner_dst_mac.replace(":", "")[6:12], 16)
                        << 8
                    ).value,
                    pkt_offset="Ether:1.dst",
                ),
                STLVmFixIpv4(offset="IP:1"),
                STLVmFixIpv4(offset="IP"),
                STLVmFixChecksumHw(
                    l3_offset="IP",
                    l4_offset="UDP",
                    l4_type=CTRexVmInsFixHwCs.L4_TYPE_UDP,
                ),
            ]
        )

        return base_pkt_a, base_pkt_b, vm1, vm2


def register():
    """Register this traffic profile to T-rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
