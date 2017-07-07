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
 - Packet: ETH / IP / UDP
 - Direction 0 --> 1:
   - Source IP address range:      10.10.10.2 - 10.10.10.11
   - Destination IP address range: 20.20.20.2 - 20.20.2011
   - Source UDP port range:        1001 - 1010
   - Destination UDP port range:   2001 - 2010
 - Direction 1 --> 0:
   - Source IP address range:      20.20.20.2 - 20.20.20.11
   - Destination IP address range: 10.10.10.2 - 10.10.10.11
   - Source UDP port range:        2001-2010
   - Destination UDP port range:   1001 - 1010
"""

from trex_stl_lib.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # IPs used in packet headers.
        self.p1_src_start_ip = '10.10.10.2'
        self.p1_src_end_ip = '10.10.10.11'
        self.p1_dst_start_ip = '20.20.20.2'
        self.p1_dst_end_ip = '20.20.20.11'

        self.p2_src_start_ip = '20.20.20.2'
        self.p2_src_end_ip = '20.20.20.11'
        self.p2_dst_start_ip = '10.10.10.2'
        self.p2_dst_end_ip = '10.10.10.11'

        # UDP ports used in packet headers.
        self.p1_src_start_udp_port = 1001
        self.p1_src_end_udp_port = 1010
        self.p1_dst_start_udp_port = 2001
        self.p1_dst_end_udp_port = 2010

        self.p2_src_start_udp_port = 2001
        self.p2_src_end_udp_port = 2010
        self.p2_dst_start_udp_port = 1001
        self.p2_dst_end_udp_port = 1010

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IP | UDP |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """

        # Direction 0 --> 1
        base_pkt_a = (Ether() /
                      IP(src=self.p1_src_start_ip,
                         dst=self.p1_dst_start_ip,
                         proto=17) /
                      UDP(sport=self.p1_src_start_udp_port,
                          dport=self.p1_dst_start_udp_port))
        # Direction 1 --> 0
        base_pkt_b = (Ether() /
                      IP(src=self.p2_src_start_ip,
                         dst=self.p2_dst_start_ip,
                         proto=17) /
                      UDP(sport=self.p2_src_start_udp_port,
                          dport=self.p2_dst_start_udp_port))

        # Direction 0 --> 1
        vm1 = STLScVmRaw([
            STLVmTupleGen(ip_min=self.p1_src_start_ip,
                          ip_max=self.p1_src_end_ip,
                          port_min=self.p1_src_start_udp_port,
                          port_max=self.p1_src_end_udp_port,
                          name="tuple1_src"),
            STLVmTupleGen(ip_min=self.p1_dst_start_ip,
                          ip_max=self.p1_dst_end_ip,
                          port_min=self.p1_dst_start_udp_port,
                          port_max=self.p1_dst_end_udp_port,
                          name="tuple1_dst"),
            STLVmWrFlowVar(fv_name="tuple1_src.ip", pkt_offset="IP.src"),
            STLVmWrFlowVar(fv_name="tuple1_dst.ip", pkt_offset="IP.dst"),
            STLVmFixIpv4(offset="IP"),
            STLVmWrFlowVar(fv_name="tuple1_src.port", pkt_offset="UDP.sport"),
            STLVmWrFlowVar(fv_name="tuple1_dst.port", pkt_offset="UDP.dport")
        ])
        # Direction 0 --> 1
        vm2 = STLScVmRaw([
            STLVmTupleGen(ip_min=self.p2_src_start_ip,
                          ip_max=self.p2_src_end_ip,
                          port_min=self.p2_src_start_udp_port,
                          port_max=self.p2_src_end_udp_port,
                          name="tuple2_src"),
            STLVmTupleGen(ip_min=self.p2_dst_start_ip,
                          ip_max=self.p2_dst_end_ip,
                          port_min=self.p2_dst_start_udp_port,
                          port_max=self.p2_dst_end_udp_port,
                          name="tuple2_dst"),
            STLVmWrFlowVar(fv_name="tuple2_src.ip", pkt_offset="IP.src"),
            STLVmWrFlowVar(fv_name="tuple2_dst.ip", pkt_offset="IP.dst"),
            STLVmFixIpv4(offset="IP"),
            STLVmWrFlowVar(fv_name="tuple2_src.port", pkt_offset="UDP.sport"),
            STLVmWrFlowVar(fv_name="tuple2_dst.port", pkt_offset="UDP.dport")
        ])

        return base_pkt_a, base_pkt_b, vm1, vm2


def register():
    """Register this traffic profile to T-rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
