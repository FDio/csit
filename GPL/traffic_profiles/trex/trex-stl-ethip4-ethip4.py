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

"""Stream profile for T-rex traffic generator.

Stream profile:
 - Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
 - Packet: ETH / IP /
 - Direction 0 --> 1:
   - Source IP address range:      10.10.10.2 - 10.10.10.254
   - Destination IP address range: 20.20.20.2
 - Direction 1 --> 0:
   - Source IP address range:      20.20.20.2 - 20.20.20.254
   - Destination IP address range: 10.10.10.2
"""

from ipaddress import IPv4Address

from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # # IPs used in packet headers.
        # self.p1_src_start_ip = u"10.10.10.2"
        # self.p1_src_end_ip = u"10.10.10.254"
        # self.p1_dst_start_ip = u"20.20.20.2"
        #
        # self.p2_src_start_ip = u"20.20.20.2"
        # self.p2_src_end_ip = u"20.20.20.254"
        # self.p2_dst_start_ip = u"10.10.10.2"

    def define_packets(self, **kwargs):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IP |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """

        p1_src_ip_start = IPv4Address(
            kwargs.get(u"p1_src_ip_start", u"10.10.10.2")
        )
        p1_src_ip_count = int(kwargs.get(u"p1_src_ip_count", 1))

        p1_dst_ip_start = IPv4Address(
            kwargs.get(u"p1_dst_ip_start", u"20.20.20.2")
        )
        p1_dst_ip_count = int(kwargs.get(u"p1_dst_ip_count", 1))

        p2_src_ip_start = IPv4Address(
            kwargs.get(u"p2_src_ip_start", u"20.20.20.2")
        )
        p2_src_ip_count = int(kwargs.get(u"p2_src_ip_count", 1))

        p2_dst_ip_start = IPv4Address(
            kwargs.get(u"p2_dst_ip_start", u"10.10.10.2")
        )
        p2_dst_ip_count = int(kwargs.get(u"p2_dst_ip_count", 1))

        # Direction 0 --> 1
        base_pkt_a = (
            Ether() /
            IP(
                src=str(p1_src_ip_start),
                dst=str(p1_dst_ip_start),
                proto=61
            )
        )
        # Direction 1 --> 0
        base_pkt_b = (
            Ether() /
            IP(
                src=str(p2_src_ip_start),
                dst=str(p2_dst_ip_start),
                proto=61
            )
        )

        # Direction 0 --> 1
        vm1 = STLScVmRaw(
            [
                STLVmFlowVar(
                    name=u"ip_src",
                    min_value=int(p1_src_ip_start),
                    max_value=int(p1_src_ip_start + p1_src_ip_count - 1),
                    size=4,
                    op=u"inc"
                ),
                STLVmWrFlowVar(
                    fv_name=u"ip_src",
                    pkt_offset=u"IP.src"
                ),
                STLVmFlowVar(
                    name=u"ip_dst",
                    min_value=int(p1_dst_ip_start),
                    max_value=int(p1_dst_ip_start + p1_dst_ip_count - 1),
                    size=4,
                    op=u"inc"
                ),
                STLVmWrFlowVar(
                    fv_name=u"ip_dst",
                    pkt_offset=u"IP.dst"
                ),
                STLVmFixIpv4(
                    offset=u"IP"
                )
            ]
        )
        # Direction 1 --> 0
        vm2 = STLScVmRaw(
            [
                STLVmFlowVar(
                    name=u"ip_src",
                    min_value=int(p2_src_ip_start),
                    max_value=int(p2_src_ip_start + p2_src_ip_count - 1),
                    size=4,
                    op=u"inc"
                ),
                STLVmWrFlowVar(
                    fv_name=u"ip_src",
                    pkt_offset=u"IP.src"
                ),
                STLVmFlowVar(
                    name=u"ip_dst",
                    min_value=int(p2_dst_ip_start),
                    max_value=int(p2_dst_ip_start + p2_dst_ip_count - 1),
                    size=4,
                    op=u"inc"
                ),
                STLVmWrFlowVar(
                    fv_name=u"ip_dst",
                    pkt_offset=u"IP.dst"
                ),
                STLVmFixIpv4(
                    offset=u"IP"
                )
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
