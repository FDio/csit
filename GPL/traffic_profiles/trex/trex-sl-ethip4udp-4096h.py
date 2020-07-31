# Copyright (c) 2020 Cisco and/or its affiliates.
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
   - Source IP address range:      192.168.0.0 - 192.255.255.255
   - Destination IP address range: 20.168.255.255 - 20.255.255.255
   - Source UDP port range:        1025
   - Destination UDP port range:   1025
 - Direction 1--> 0:
   - Source IP address range:      20.168.0.0 - 20.255.255.255
   - Destination IP address range: 68.142.68.0 - 68.142.68.3
   - Source UDP port range:        1025
   - Destination UDP port range:   1025
"""

from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        self.limit_flows = 262048

        # IPs used in packet headers.
        self.p1_src_start_ip = u"192.168.0.0"
        self.p1_src_end_ip = u"192.255.255.255"
        self.p1_dst_start_ip = u"20.0.0.0"
        self.p1_dst_end_ip = u"20.255.255.255"

        self.p2_src_start_ip = u"20.0.0.0"
        self.p2_src_end_ip = u"20.255.255.255"
        self.p2_dst_start_ip = u"68.142.68.0"
        self.p2_dst_end_ip = u"68.142.68.3"

        # UDP ports used in packet headers.
        self.p1_src_start_udp_port = 1025
        self.p1_src_end_udp_port = 1025
        self.p1_dst_start_udp_port = 1025
        self.p1_dst_end_udp_port = 1025

        self.p2_src_start_udp_port = 1025
        self.p2_src_end_udp_port = 1025
        self.p2_dst_start_udp_port = 1025
        self.p2_dst_end_udp_port = 65535

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
                src=self.p1_src_start_ip,
                dst=self.p1_dst_start_ip,
                proto=17
            ) /
            UDP(
                sport=self.p1_src_start_udp_port,
                dport=self.p1_dst_start_udp_port
            )
        )
        # Direction 1 --> 0
        base_pkt_b = (
            Ether() /
            IP(
                src=self.p2_src_start_ip,
                dst=self.p2_dst_start_ip,
                proto=17
            ) /
            UDP(
                sport=self.p2_src_start_udp_port,
                dport=self.p2_dst_start_udp_port
            )
        )

        # Direction 0 --> 1
        vm1 = STLScVmRaw(
            [
                STLVmTupleGen(
                    ip_min=self.p1_src_start_ip,
                    ip_max=self.p1_src_end_ip,
                    port_min=self.p1_src_start_udp_port,
                    port_max=self.p1_src_end_udp_port,
                    name=u"stuple",
                    limit_flows=self.limit_flows
                ),
                STLVmWrFlowVar(
                    fv_name=u"stuple.ip",
                    pkt_offset=u"IP.src"
                ),
                STLVmFixIpv4(
                    offset=u"IP"
                ),
                STLVmWrFlowVar(
                    fv_name=u"stuple.port",
                    pkt_offset=u"UDP.sport"
                ),
                STLVmTupleGen(
                    ip_min=self.p1_dst_start_ip,
                    ip_max=self.p1_dst_end_ip,
                    port_min=self.p1_dst_start_udp_port,
                    port_max=self.p1_dst_end_udp_port,
                    name=u"dtuple",
                    limit_flows=self.limit_flows
                ),
                STLVmWrFlowVar(
                    fv_name=u"dtuple.ip",
                    pkt_offset=u"IP.dst"
                ),
                STLVmFixIpv4(
                    offset=u"IP"
                ),
                STLVmWrFlowVar(
                    fv_name=u"dtuple.port",
                    pkt_offset=u"UDP.dport"
                )
            ]
        )

        # Direction 1 --> 0
        vm2 = STLScVmRaw(
            [
                STLVmTupleGen(
                    ip_min=self.p2_src_start_ip,
                    ip_max=self.p2_src_end_ip,
                    port_min=self.p2_src_start_udp_port,
                    port_max=self.p2_src_end_udp_port,
                    name=u"stuple",
                    limit_flows=self.limit_flows
                ),
                STLVmWrFlowVar(
                    fv_name=u"stuple.ip",
                    pkt_offset=u"IP.src"
                ),
                STLVmFixIpv4(
                    offset=u"IP"
                ),
                STLVmWrFlowVar(
                    fv_name=u"stuple.port",
                    pkt_offset=u"UDP.sport"
                )
            ]
        )

        return base_pkt_a, base_pkt_b, vm1, vm2


def register():
    """Register this traffic profile to T-Rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()