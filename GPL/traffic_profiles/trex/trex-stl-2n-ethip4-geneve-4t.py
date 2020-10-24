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
 - Direction 0 --> 1:
   - Packet: ETH / IP
   - Source IP address range:            10.32.1.0 - 10.32.1.255
   - Destination IP address range:       10.16.1.0 - 10.16.1.255
 - Direction 1 --> 0:
   - Packet: ETH / IP / UDP / GENEVE / ETH / IP
   - Outer Source IP address range:      1.1.1.1
   - Outer Destination IP address range: 1.1.1.2
   - Inner Source IP address range:      10.16.1.0 - 10.16.1.255
   - Inner Destination IP address range: 10.32.1.0 - 10.32.1.255
   - Source UDP port range:              6081
   - Destination UDP port range:         6081
"""

from trex.stl.api import *

from contrib.geneve import GENEVE
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # IPs used in packet headers of Direction 0 --> 1.
        self.p1_src_start_ip = u"10.32.1.0"
        self.p1_src_end_ip = u"10.32.4.255"
        self.p1_dst_start_ip = u"10.16.1.0"
        self.p1_dst_end_ip = u"10.16.4.255"

        # IPs used in packet headers of Direction 1 --> 0.
        self.p2_outer_src_ip = u"1.1.1.1"
        self.p2_outer_dst_ip = u"1.1.1.2"

        self.p2_inner_src_start_ip = u"10.16.1.0"
        self.p2_inner_src_end_ip = u"10.16.4.255"
        self.p2_inner_dst_start_ip = u"10.32.1.0"
        self.p2_inner_dst_end_ip = u"10.32.4.255"

        # MACs used in inner ethernet header of Direction 1 --> 0.
        # self.p2_inner_src_mac = u""
        self.p2_inner_dst_mac = u"d0:0b:ee:d0:00:00"

        # UDP ports used in packet headers of Direction 1 --> 0.
        self.p2_src_udp_port = 6081
        self.p2_dst_udp_port = 6081

        # VNIs used in GENEVE headers of Direction 1 --> 0.
        self.p2_geneve_start_vni = 1

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
                proto=61
            )
        )
        # Direction 1 --> 0
        base_pkt_b = (
            Ether() /
            IP(
                src=self.p2_outer_src_ip,
                dst=self.p2_outer_dst_ip,
                proto=17
            ) /
            UDP(
                sport=self.p2_src_udp_port,
                dport=self.p2_dst_udp_port
            ) /
            GENEVE(vni=self.p2_geneve_start_vni) /

            Ether(dst=self.p2_inner_dst_mac) /
            IP(
                src=self.p2_inner_src_start_ip,
                dst=self.p1_dst_start_ip,
                proto=61
            )
        )
        base_pkt_b /= Raw(load=(110 - len(base_pkt_b))*b"0")
        # Direction 0 --> 1
        vm1 = STLScVmRaw(
            [
                STLVmFlowVar(
                    name=u"ip_src",
                    min_value=self.p1_src_start_ip,
                    max_value=self.p1_src_end_ip,
                    size=4,
                    op=u"inc"
                ),
                STLVmWrFlowVar(
                    fv_name=u"ip_src",
                    pkt_offset=u"IP.src"
                ),
                STLVmFlowVar(
                    name=u"ip_dst",
                    min_value=self.p1_dst_start_ip,
                    max_value=self.p1_dst_end_ip,
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
                # generate 4th (ip variable) and 3rd (port variable) bytes of
                # IP:1.src and IP:1.dst; port variable is equal to required
                # GENEVE.vni too
                STLVmTupleGen(
                    ip_min=0,
                    ip_max=255,
                    port_min=1,
                    port_max=4,
                    name=u"ip_tupple"
                ),
                STLVmWrFlowVar(
                    fv_name=u"ip_tupple.port",
                    pkt_offset=u"IP:1.src",
                    offset_fixup=2
                ),
                STLVmWrFlowVar(
                    fv_name=u"ip_tupple.port",
                    pkt_offset=u"IP:1.dst",
                    offset_fixup=2
                ),
                # STLVmWrFlowVar(
                #     fv_name=u"ip_tupple.ip",
                #     pkt_offset=u"IP:1.src",
                #     offset_fixup=3
                # ),
                # STLVmWrFlowVar(
                #     fv_name=u"ip_tupple.ip",
                #     pkt_offset=u"IP:1.dst",
                #     offset_fixup=3
                # ),
                # STLVmWrMaskFlowVar(
                #     fv_name=u"ip_tupple.port",
                #     pkt_cast_size=4,
                #     mask=0x0000ff00,
                #     pkt_offset=u"IP:1.src"
                # ),
                # STLVmWrMaskFlowVar(
                #     fv_name=u"ip_tupple.port",
                #     pkt_cast_size=4,
                #     mask=0x0000ff00,
                #     pkt_offset=u"IP:1.dst"
                # ),
                STLVmWrMaskFlowVar(
                    fv_name=u"ip_tupple.ip",
                    pkt_cast_size=4,
                    mask=0x000000ff,
                    pkt_offset=u"IP:1.ip"
                ),
                STLVmWrMaskFlowVar(
                    fv_name=u"ip_tupple.ip",
                    pkt_cast_size=4,
                    mask=0x000000ff,
                    pkt_offset=u"IP:1.dst"
                ),
                STLVmWrFlowVar(
                    fv_name=u"ip_tupple.port",
                    pkt_offset=u"GENEVE.vni",
                    offset_fixup=1
                ),
                # generate 6th byte (port variable) of Ether:1.dst; ip variable
                # used just to synchronise with inner IPs and GENEVE.vni
                STLVmTupleGen(
                    ip_min=0,
                    ip_max=255,
                    port_min=0,
                    port_max=3,
                    name=u"mac_tupple"
                ),
                STLVmWrFlowVar(
                    fv_name=u"mac_tupple.port",
                    pkt_offset=u"Ether:1.dst",
                    offset_fixup=5
                ),
                # STLVmFlowVar(
                #     name=u"inner_ip_src",
                #     min_value=self.p2_inner_src_start_ip,
                #     max_value=self.p2_inner_src_end_ip,
                #     size=4,
                #     op=u"inc"
                # ),
                # STLVmWrFlowVar(
                #     fv_name=u"inner_ip_src",
                #     pkt_offset=u"IP:1.src"
                # ),
                # STLVmFlowVar(
                #     name=u"inner_ip_dst",
                #     min_value=self.p2_inner_dst_start_ip,
                #     max_value=self.p2_inner_dst_end_ip,
                #     size=4,
                #     op=u"inc"
                # ),
                # STLVmWrFlowVar(
                #     fv_name=u"inner_ip_dst",
                #     pkt_offset=u"IP:1.dst"
                # ),
                STLVmFixIpv4(
                    offset=u"IP:1"
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
