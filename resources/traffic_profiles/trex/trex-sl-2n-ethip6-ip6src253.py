# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""Stream profile for T-rex traffic generator.

Stream profile:
 - Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
 - Packet: ETH / IPv6 /
 - Direction 0 --> 1:
   - Source IP address range:      2001:1::2 - 2001:1::FE
   - Destination IP address range: 2001:2::2
 - Direction 1 --> 0:
   - Source IP address range:      2001:2::2 - 2001:2::FE
   - Destination IP address range: 2001:1::2
"""

from trex_stl_lib.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

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
        base_pkt_a = Ether() / IPv6(src=self.p1_src_start_ip,
                                    dst=self.p1_dst_start_ip)
        # Direction 1 --> 0
        base_pkt_b = Ether() / IPv6(src=self.p2_src_start_ip,
                                    dst=self.p2_dst_start_ip)

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

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
