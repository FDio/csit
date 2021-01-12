# Copyright (c) 2020 Cisco and/or its affiliates.
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
 - Packet: ETH / IP / UDP
 - Direction 0 --> 1:
   - Source IP address range:      20.0.0.0
   - Destination IP address range: 30.0.0.0
   - Source UDP port range:        1024
   - Destination UDP port range:   1024
 - Direction 1 --> 0:
   - Source IP address range:      30.0.0.0
   - Destination IP address range: 200.0.0.0
   - Source UDP port range:        1024
   - Destination UDP port range:   1028
"""

from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # IPs used in packet headers.
        self.p1_src_ip = u"20.0.0.0"
        self.p1_dst_ip = u"30.0.0.0"

        self.p2_src_ip = u"30.0.0.0"
        self.p2_dst_ip = u"200.0.0.0"

        # UDP ports used in packet headers.
        self.p1_src_udp_port = 1024
        self.p1_dst_udp_port = 1024

        self.p2_src_udp_port = 1024
        self.p2_dst_udp_port = 2048

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IP | UDP |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """

        # Direction 0 --> 1
        base_pkt_a = (
            Ether() /
            IP(
                src=self.p1_src_ip,
                dst=self.p1_dst_ip,
                proto=17
            ) /
            UDP(
                sport=self.p1_src_udp_port,
                dport=self.p1_dst_udp_port
            )
        )
        # Direction 1 --> 0
        base_pkt_b = (
            Ether() /
            IP(
                src=self.p2_src_ip,
                dst=self.p2_dst_ip,
                proto=17
            ) /
            UDP(
                sport=self.p2_src_udp_port,
                dport=self.p2_dst_udp_port
            )
        )

        return base_pkt_a, base_pkt_b, None, None


def register():
    """Register this traffic profile to T-rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
