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
   - Source IP address range:      20.0.0.0 - 20.0.0.0
   - Destination IP address range: 12.0.0.2 - 12.0.0.2
   - Source UDP port range:        1024 - 1024
   - Destination UDP port range:   1024 - 1024
 - Direction 1 --> 0:
   - Source IP address range:      12.0.0.2 - 12.0.0.2
   - Destination IP address range: 200.0.0.0 - 200.0.0.0
   - Source UDP port range:        1024 - 1024
   - Destination UDP port range:   1028 - 1028

"""

from random import choice
from string import letters
from trex_stl_lib.api import *


class TrafficStreams(object):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters.
        """

        # Default value of frame size, it will be overwritten by the value of
        # "framesize" parameter of "get_streams" method.
        self.framesize = 64

        # If needed, add your own parameters.

        # IPs used in packet headers.
        # Set your own.
        self.p1_src_start_ip = '20.0.0.0'
        self.p1_src_end_ip = '20.0.0.0'
        self.p1_dst_start_ip = '12.0.0.2'

        self.p2_src_start_ip = '12.0.0.2'
        self.p2_src_end_ip = '12.0.0.2'
        self.p2_dst_start_ip = '200.0.0.0'

        # UDP ports used in packet headers.
        # Set your own.
        self.p1_src_start_udp_port = 1024
        self.p1_dst_start_udp_port = 1024

        self.p2_src_start_udp_port = 1024
        self.p2_dst_start_udp_port = 1028

        # Definition of IMIX.
        # Do not change.
        self.stream_table = {
            'IMIX_v4': [
                {'size': 60, 'pps': 28, 'isg': 0},
                {'size': 590, 'pps': 20, 'isg': 0.1},
                {'size': 1514, 'pps': 4, 'isg': 0.2}
            ],
            'IMIX_v4_1': [
                {'size': 64, 'pps': 28, 'isg': 0},
                {'size': 570, 'pps': 16, 'isg': 0.1},
                {'size': 1518, 'pps': 4, 'isg': 0.2}
            ]
        }

    @staticmethod
    def _gen_payload(length):
        """Generate payload.

        If needed, implement your own algorithm.

        :param length: Length of generated payload.
        :type length: int
        :returns: Payload.
        :rtype: str
        """

        payload = ""
        for _ in range(length):
            payload += choice(letters)

        return payload

    def create_streams(self):
        """Create traffic streams.

        Implement your own traffic streams.

        :returns: Traffic streams.
        :rtype: list
        """

        # Packet definition: | ETH | IP | UDP |
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

        # Field Engine program to change fields within the packets.
        # Direction 0 --> 1
        # vm1 = STLScVmRaw([STLVmFlowVar(name="src",
        #                                min_value=self.p1_src_start_ip,
        #                                max_value=self.p1_src_end_ip,
        #                                size=4, op="inc"),
        #                   STLVmWrFlowVar(fv_name="src",
        #                                  pkt_offset="IP.src"),
        #                   STLVmFixIpv4(offset="IP"),
        #                   ], split_by_field="src")
        # # Direction 1 --> 0
        # vm2 = STLScVmRaw([STLVmFlowVar(name="src",
        #                                min_value=self.p2_src_start_ip,
        #                                max_value=self.p2_src_end_ip,
        #                                size=4, op="inc"),
        #                   STLVmWrFlowVar(fv_name="src",
        #                                  pkt_offset="IP.src"),
        #                   STLVmFixIpv4(offset="IP"),
        #                   ], split_by_field="src")

        # In most cases you will not have to change the code below:

        # Frame size is defined as an integer, e.g. 64, 1518:
        if isinstance(self.framesize, int):

            # Create a base packet and pad it to size
            fsize_no_fcs = self.framesize - 4

            # Direction 0 --> 1
            pkt_a = STLPktBuilder(
                pkt=base_pkt_a /
                TrafficStreams._gen_payload(
                    max(0, fsize_no_fcs - len(base_pkt_a))))#,
                #vm=vm1)
            # Direction 1 --> 0
            pkt_b = STLPktBuilder(
                pkt=base_pkt_b / ("x" * max(0, fsize_no_fcs - len(base_pkt_b))))
                # TrafficStreams._gen_payload(
                #     max(0, fsize_no_fcs - len(base_pkt_b))))#,
                #vm=vm2)

            # Packets for latency measurement:
            # Direction 0 --> 1
            pkt_lat_a = STLPktBuilder(
                pkt=base_pkt_a / ("x" * max(0, fsize_no_fcs - len(base_pkt_a))))
                # TrafficStreams._gen_payload(
                #     max(0, fsize_no_fcs - len(base_pkt_a))))
            # Direction 1 --> 0
            pkt_lat_b = STLPktBuilder(
                pkt=base_pkt_b / ("x" * max(0, fsize_no_fcs - len(base_pkt_b))))
                # TrafficStreams._gen_payload(
                #     max(0, fsize_no_fcs - len(base_pkt_b))))

            # Create the streams:
            # Direction 0 --> 1
            stream1 = STLStream(packet=pkt_a,
                                mode = STLTXCont(pps=9000))
            # Direction 1 --> 0
            # second traffic stream with a phase of 10ns (inter-stream gap)
            stream2 = STLStream(packet=pkt_b,
                                isg=10.0,
                                mode = STLTXCont(pps=9000))

            # Streams for latency measurement:
            # Direction 0 --> 1
            lat_stream1 = STLStream(packet=pkt_lat_a,
                                    flow_stats=STLFlowLatencyStats(pg_id=0),
                                    mode=STLTXCont(pps=9000))
            # Direction 1 --> 0
            # second traffic stream with a phase of 10ns (inter-stream gap)
            lat_stream2 = STLStream(packet=pkt_lat_b,
                                    isg=10.0,
                                    flow_stats=STLFlowLatencyStats(pg_id=1),
                                    mode=STLTXCont(pps=9000))

            return [stream1, stream2, lat_stream1, lat_stream2]

        # Frame size is defined as a string, e.g.IMIX_v4_1:
        elif (isinstance(self.framesize, str) or
              isinstance(self.framesize, basestring)):

            stream1 = []
            stream2 = []

            for stream in self.stream_table[self.framesize]:
                fsize_no_fcs = stream['size'] - 4  # without FCS
                # Create a base packet and pad it to size
                pkt_a = STLPktBuilder(
                    pkt=base_pkt_a /
                    TrafficStreams._gen_payload(
                        max(0, fsize_no_fcs - len(base_pkt_a))),
                    vm=vm1)
                pkt_b = STLPktBuilder(
                    pkt=base_pkt_b /
                    TrafficStreams._gen_payload(
                        max(0, fsize_no_fcs - len(base_pkt_b))),
                    vm=vm2)

                # Create the streams:
                stream1.append(STLStream(packet=pkt_a,
                                         isg=stream['isg'],
                                         mode=STLTXCont(pps=stream['pps'])))
                stream2.append(STLStream(packet=pkt_b,
                                         isg=stream['isg'],
                                         mode=STLTXCont(pps=stream['pps'])))
            streams = list()
            streams.extend(stream1)
            streams.extend(stream2)

            return streams

    def get_streams(self, **kwargs):
        """Get traffic streams created by "create_streams" method.

        If needed, add your own parameters.

        :param kwargs: Key-value pairs used by "create_streams" method while
        creating streams.
        :returns: Traffic streams.
        :rtype: list
        """

        self.framesize = kwargs['framesize']

        return self.create_streams()


def register():
    """Register this traffic profile to T-rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
