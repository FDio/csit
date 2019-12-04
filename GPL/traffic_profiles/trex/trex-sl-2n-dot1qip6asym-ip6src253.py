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

"""Stream profile for T-rex traffic generator.

Stream profile:
 - Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
 - Direction 0 --> 1:
   - Packet: ETH / IPv6 /
   - Source IP address range:      2001:1::2 - 2001:1::FE
   - Destination IP address range: 2001:2::2
 - Direction 1 --> 0:
   - Packet: ETH / DOT1Q / IPv6 /
   - Source IP address range:      2001:2::2 - 2001:2::FE
   - Destination IP address range: 2001:1::2
"""

from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # VLAN ID
        self.vlan_id = 10

        # IPs used in packet headers.
        self.p1_src_start_ip = '2001:1::2'
        self.p1_src_end_ip = '2001:1::FE'
        self.p1_dst_start_ip = '2001:2::2'

        self.p2_src_start_ip = '2001:2::2'
        self.p2_src_end_ip = '2001:2::FE'
        self.p2_dst_start_ip = '2001:1::2'

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IPv6 |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """

        base_p1, count_p1 = self._get_start_end_ipv6(self.p1_src_start_ip,
                                                     self.p1_src_end_ip)
        base_p2, count_p2 = self._get_start_end_ipv6(self.p2_src_start_ip,
                                                     self.p2_src_end_ip)

        # Direction 0 --> 1
        base_pkt_a = (Ether() /
                      IPv6(src=self.p1_src_start_ip,
                           dst=self.p1_dst_start_ip))
        # Direction 1 --> 0
        base_pkt_b = (Ether() /
                      Dot1Q(vlan=self.vlan_id) /
                      IPv6(src=self.p2_src_start_ip,
                           dst=self.p2_dst_start_ip))

        # Direction 0 --> 1
        vm1 = STLScVmRaw([STLVmFlowVar(name="ipv6_src",
                                       min_value=base_p1,
                                       max_value=base_p1 + count_p1,
                                       size=8, op="inc"),
                          STLVmWrFlowVar(fv_name="ipv6_src",
                                         pkt_offset="IPv6.src",
                                         offset_fixup=8)])
        # Direction 1 --> 0
        vm2 = STLScVmRaw([STLVmFlowVar(name="ipv6_src",
                                       min_value=base_p2,
                                       max_value=base_p2 + count_p2,
                                       size=8, op="inc"),
                          STLVmWrFlowVar(fv_name="ipv6_src",
                                         pkt_offset="IPv6.src",
                                         offset_fixup=8)])

        return base_pkt_a, base_pkt_b, vm1, vm2


def register():
    """Register this traffic profile to T-rex.

    Do not change this function.

    :returns: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
