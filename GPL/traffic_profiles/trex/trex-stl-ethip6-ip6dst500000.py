# Copyright (c) 2023 Intel and/or its affiliates.
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
 - Packet: ETH / IPv6 /
 - Direction 0 --> 1:
   - Source IP address range:      2001:1::1
   - Destination IP address range: 2001:2::0 - 2001:2::7:a11f
 - Direction 1 --> 0:
   - Source IP address range:      2001:2::1
   - Destination IP address range: 2001:1::0 - 2001:1::7:a11f
"""

from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # IPs used in packet headers.
        self.p1_src_start_ip = u"2001:1::1"
        self.p1_dst_start_ip = u"2001:2::0"
        self.p1_dst_end_ip = u"2001:2::7:a11f"

        self.p2_src_start_ip = u"2001:2::1"
        self.p2_dst_start_ip = u"2001:1::0"
        self.p2_dst_end_ip = u"2001:1::7:a11f"

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IPv6 |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """

        base_p1, count_p1 = self._get_start_end_ipv6(
            self.p1_dst_start_ip,
            self.p1_dst_end_ip
        )
        base_p2, count_p2 = self._get_start_end_ipv6(
            self.p2_dst_start_ip,
            self.p2_dst_end_ip
        )

        # Direction 0 --> 1
        base_pkt_a = (
            Ether() /
            IPv6(
                src=self.p1_src_start_ip,
                dst=self.p1_dst_start_ip
            )
        )
        # Direction 1 --> 0
        base_pkt_b = (
            Ether() /
            IPv6(
                src=self.p2_src_start_ip,
                dst=self.p2_dst_start_ip
            )
        )

        # Direction 0 --> 1
        vm1 = STLScVmRaw(
            [
                STLVmFlowVar(
                    name=u"ipv6_dst",
                    min_value=base_p1,
                    max_value=base_p1 + count_p1,
                    size=8,
                    op=u"inc"
                ),
                STLVmWrFlowVar(
                    fv_name=u"ipv6_dst",
                    pkt_offset=u"IPv6.dst",
                    offset_fixup=8
                )
            ]
        )
        # Direction 1 --> 0
        vm2 = STLScVmRaw(
            [
                STLVmFlowVar(
                    name=u"ipv6_dst",
                    min_value=base_p2,
                    max_value=base_p2 + count_p2,
                    size=8,
                    op=u"inc"
                ),
                STLVmWrFlowVar(
                    fv_name=u"ipv6_dst",
                    pkt_offset=u"IPv6.dst",
                    offset_fixup=8
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
