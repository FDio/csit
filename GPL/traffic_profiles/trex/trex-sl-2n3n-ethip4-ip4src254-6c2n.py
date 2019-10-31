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
 - Packet: ETH / IP /
 - Direction 0 --> 1:
   - Destination MAC address: 52:54:00:00:nf_id:01
   - Source IP address range:      10.10.10.1 - 10.10.10.254
   - Destination IP address range: 20.20.20.1
 - Direction 1 --> 0:
    - Destination MAC address: 52:54:00:00:nf_id:02
   - Source IP address range:      20.20.20.1 - 20.20.20.254
   - Destination IP address range: 10.10.10.1
"""

from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # Service density parameters.
        self.nf_chains = 6
        self.nf_nodes = 2

        # MACs used in packet headers.
        self.p1_dst_start_mac = '52:54:00:00:00:01'
        self.p2_dst_start_mac = '52:54:00:00:00:02'

        # IPs used in packet headers.
        self.p1_src_start_ip = '10.10.10.1'
        self.p1_src_end_ip = '10.10.10.254'
        self.p1_dst_start_ip = '20.20.20.1'

        self.p2_src_start_ip = '20.20.20.1'
        self.p2_src_end_ip = '20.20.20.254'
        self.p2_dst_start_ip = '10.10.10.1'

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IP |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """

        # Direction 0 --> 1
        base_pkt_a = (Ether(dst=self.p1_dst_start_mac) /
                      IP(src=self.p1_src_start_ip,
                         dst=self.p1_dst_start_ip,
                         proto=61))
        # Direction 1 --> 0
        base_pkt_b = (Ether(dst=self.p2_dst_start_mac) /
                      IP(src=self.p2_src_start_ip,
                         dst=self.p2_dst_start_ip,
                         proto=61))

        # Direction 0 --> 1
        vm1 = STLScVmRaw([STLVmFlowVar(name="mac_dst",
                                       min_value=1,
                                       max_value=self.nf_chains*self.nf_nodes,
                                       size=1, step=self.nf_nodes, op="inc"),
                          STLVmWrFlowVar(fv_name="mac_dst", pkt_offset=4),
                          STLVmFlowVar(name="src",
                                       min_value=self.p1_src_start_ip,
                                       max_value=self.p1_src_end_ip,
                                       size=4, op="inc"),
                          STLVmWrFlowVar(fv_name="src", pkt_offset="IP.src"),
                          STLVmFixIpv4(offset="IP")])
        # Direction 1 --> 0
        vm2 = STLScVmRaw([STLVmFlowVar(name="mac_dst",
                                       min_value=self.nf_nodes,
                                       max_value=self.nf_chains*self.nf_nodes,
                                       size=1, step=self.nf_nodes, op="inc"),
                          STLVmWrFlowVar(fv_name="mac_dst", pkt_offset=4),
                          STLVmFlowVar(name="src",
                                       min_value=self.p2_src_start_ip,
                                       max_value=self.p2_src_end_ip,
                                       size=4, op="inc"),
                          STLVmWrFlowVar(fv_name="src", pkt_offset="IP.src"),
                          STLVmFixIpv4(offset="IP")])

        return base_pkt_a, base_pkt_b, vm1, vm2


def register():
    """Register this traffic profile to T-rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
