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
 - Packet: ETH / IP /
 - Direction 0 --> 1:
   - Source IP address range:      10.10.10.2 - 10.10.10.254
   - Destination IP address range: 20.20.20.2
 - Direction 1 --> 0:
   - Source IP address range:      20.20.20.2 - 20.20.20.254
   - Destination IP address range: 10.10.10.2
"""

from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # IPs used in packet headers.
        self.p1_src_start_ip = u"20.0.0.0"
        self.p1_dst_start_ip = u"12.0.0.0"

        self.p2_src_start_ip = u"12.0.0.0"
        self.p2_dst_start_ip = u"200.0.0.0"

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IP |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """
        flows = 1000
        burst_sec=10
        inter_burst_gap=10
        streams_per_second=10

        streams = streams_per_second * (burst_sec + inter_burst_gap)
        flows_per_stream = int(flows / streams)

        base_pkt_a = list()
        base_pkt_b = list()

        for stream in range(streams):

            # Direction 0 --> 1
            base_pkt_a_item = (
                Ether() /
                IP(
                    src=self.p1_src_start_ip,
                    dst=self.p1_dst_start_ip
                ) /
                UDP(sport=1024+stream, dport=0)
            )
            base_pkt_a.append(base_pkt_a_item)

            # Direction 1 --> 0
            base_pkt_b_item = (
                Ether() /
                IP(
                    src=self.p2_src_start_ip,
                    dst=self.p2_dst_start_ip
                ) /
                UDP(sport=0, dport=1024+stream)
            )
            base_pkt_b.append(base_pkt_b_item)

        # Direction 0 --> 1
        vm1 = STLVM()
        vm1.var(name=u"sport",
                min_value=1024,
                max_value=1024+flows_per_stream,
                size=2,
                op=u"random")
        vm1.write(fv_name="sport", pkt_offset="UDP.sport")

        # Direction 1 --> 0
        vm2 = STLVM()
        vm2.var(name=u"dport",
                min_value=1024,
                max_value=1024+flows_per_stream,
                size=2,
                op=u"random")
        vm1.write(fv_name="dport", pkt_offset="UDP.dport")

        return base_pkt_a, base_pkt_b, vm1, vm2


def register():
    """Register this traffic profile to T-rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
