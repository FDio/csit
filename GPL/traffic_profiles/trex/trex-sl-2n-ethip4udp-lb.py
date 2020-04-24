# Copyright (c) 2020 Intel and/or its affiliates.
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
 - Packet: ETH / IP / UDP
 - Direction 0 --> 1:
   - Source IP address range:      192.168.50.74 - 192.168.50.79
   - Destination IP address range: 90.1.2.1
 - Direction 1 --> 0:
   - Source IP address range:      192.168.60.74 - 192.168.60.79
   - Destination IP address range: 192.168.50.74 - 192.168.50.79
"""

from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # IPs used in packet headers.
        self.p1_src_start_ip = u"192.168.50.74"
        self.p1_src_end_ip = u"192.168.50.79"
        self.p1_dst_start_ip = u"90.1.2.1"

        self.p2_src_start_ip = u"192.168.60.74"
        self.p2_src_end_ip = u"192.168.60.79"
        self.p2_dst_start_ip = u"192.168.50.74"
        self.p2_dst_end_ip = u"192.168.50.79"

        # UDP ports used in packet headers.
        self.p1_src_udp_port = 63
        self.p1_dst_udp_port = 20000

        self.p2_src_udp_port = 3307
        self.p2_dst_udp_port = 63

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IP | UDP

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """

        # Direction 0 --> 1
        base_pkt_a = (
            Ether() /
            IP(
                src=self.p1_src_start_ip,
                dst=self.p1_dst_start_ip,
                proto=17) /
            UDP(
                sport=self.p1_src_udp_port,
                dport=self.p1_dst_udp_port
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
                sport=self.p2_src_udp_port,
                dport=self.p2_dst_udp_port
             )
        )

        # Direction 0 --> 1
        vm1 = STLScVmRaw(
            [
                STLVmFlowVar(
                    name=u"src",
                    min_value=self.p1_src_start_ip,
                    max_value=self.p1_src_end_ip,
                    size=4,
                    op=u"inc"
                ),
                STLVmWrFlowVar(
                    fv_name=u"src",
                    pkt_offset=u"IP.src"
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
                    name=u"src",
                    min_value=self.p2_src_start_ip,
                    max_value=self.p2_src_end_ip,
                    size=4,
                    op=u"inc"
                ),
                STLVmWrFlowVar(
                    fv_name=u"src",
                    pkt_offset=u"IP.src"
                ),
                STLVmFlowVar(
                    name=u"dst",
                    min_value=self.p2_dst_start_ip,
                    max_value=self.p2_dst_end_ip,
                    size=4,
                    op=u"inc"
                ),
                STLVmWrFlowVar(
                    fv_name=u"dst",
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
