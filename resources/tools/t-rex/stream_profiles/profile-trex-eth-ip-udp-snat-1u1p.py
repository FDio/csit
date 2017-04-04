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

"""

"""

from random import choice
from string import letters
from trex_stl_lib.api import *


class STLProfile(object):
    """

    """

    def __init__(self):
        """

        """

        self.p1_src_start_ip = '20.0.0.0'
        self.p1_src_end_ip = '20.0.0.0'
        self.p1_dst_start_ip = '12.0.0.2'

        self.p2_src_start_ip = '12.0.0.2'
        self.p2_src_end_ip = '12.0.0.2'
        self.p2_dst_start_ip = '200.0.0.0'

        self.p1_src_start_udp_port = 1024
        self.p1_dst_start_udp_port = 1024

        self.p2_src_start_udp_port = 1024
        self.p2_dst_start_udp_port = 1028

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
        """

        :param length:
        :returns:
        """

        payload = ""
        for i in range(length):
            payload += choice(letters)

        return payload

    def create_streams(self, framesize):
        """

        :param framesize:
        :returns:
        :raises TypeError:
        """

        base_pkt_a = (Ether() /
                      IP(src=self.p1_src_start_ip,
                         dst=self.p1_dst_start_ip,
                         proto=17) /
                      UDP(sport=int(self.p1_src_start_udp_port),
                          dport=int(self.p1_dst_start_udp_port)))
        base_pkt_b = (Ether() /
                      IP(src=self.p2_src_start_ip,
                         dst=self.p2_dst_start_ip,
                         proto=17) /
                      UDP(sport=int(self.p2_src_start_udp_port),
                          dport=int(self.p2_dst_start_udp_port)))

        vm1 = STLScVmRaw([STLVmFlowVar(name="src",
                                       min_value=self.p1_src_start_ip,
                                       max_value=self.p1_src_end_ip,
                                       size=4, op="inc"),
                          STLVmWrFlowVar(fv_name="src",
                                         pkt_offset="IP.src"),
                          STLVmFixIpv4(offset="IP"),
                          ], split_by_field="src")
        vm2 = STLScVmRaw([STLVmFlowVar(name="src",
                                       min_value=self.p2_src_start_ip,
                                       max_value=self.p2_src_end_ip,
                                       size=4, op="inc"),
                          STLVmWrFlowVar(fv_name="src",
                                         pkt_offset="IP.src"),
                          STLVmFixIpv4(offset="IP"),
                          ], split_by_field="src")

        if isinstance(framesize, int):

            fsize_no_fcs = framesize - 4  # without FCS
            pkt_a = STLPktBuilder(
                pkt=base_pkt_a /
                self._gen_payload(max(0, fsize_no_fcs - len(base_pkt_a))),
                vm=vm1)
            pkt_b = STLPktBuilder(
                pkt=base_pkt_b /
                self._gen_payload(max(0, fsize_no_fcs - len(base_pkt_b))),
                vm=vm2)
            pkt_lat_a = STLPktBuilder(
                pkt=base_pkt_a /
                self._gen_payload(max(0, fsize_no_fcs - len(base_pkt_a))))
            pkt_lat_b = STLPktBuilder(
                pkt=base_pkt_b /
                self._gen_payload(max(0, fsize_no_fcs - len(base_pkt_b))))

            stream1 = STLStream(packet=pkt_a,
                                mode=STLTXCont(pps=9000))
            # second traffic stream with a phase of 10ns (inter-stream gap)
            stream2 = STLStream(packet=pkt_b,
                                isg=10.0,
                                mode=STLTXCont(pps=9000))

            lat_stream1 = STLStream(packet=pkt_lat_a,
                                    flow_stats=STLFlowLatencyStats(pg_id=0),
                                    mode=STLTXCont(pps=9000))
            # second traffic stream with a phase of 10ns (inter-stream gap)
            lat_stream2 = STLStream(packet=pkt_lat_b,
                                    isg=10.0,
                                    flow_stats=STLFlowLatencyStats(pg_id=1),
                                    mode=STLTXCont(pps=9000))

        elif isinstance(framesize, str) or isinstance(framesize, basestring):

            stream1 = []
            stream2 = []
            lat_stream1 = []
            lat_stream2 = []

            for stream in self.stream_table[framesize]:
                fsize_no_fcs = stream['size'] - 4  # without FCS
                pkt_a = STLPktBuilder(
                    pkt=base_pkt_a /
                    self._gen_payload(max(0, fsize_no_fcs - len(base_pkt_a))),
                    vm=vm1)
                pkt_b = STLPktBuilder(
                    pkt=base_pkt_b /
                    self._gen_payload(max(0, fsize_no_fcs - len(base_pkt_b))),
                    vm=vm2)

                stream1.append(STLStream(packet=pkt_a,
                                         isg=stream['isg'],
                                         mode=STLTXCont(pps=stream['pps'])))
                stream2.append(STLStream(packet=pkt_b,
                                         isg=stream['isg'],
                                         mode=STLTXCont(pps=stream['pps'])))

        else:
            raise TypeError("Framesize can be either integer (e.g. 64, 1518) "
                            "or string (e.g. 'IMIX_v4_1').")

        return stream1, stream2, lat_stream1, lat_stream2

    def get_streams(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        return [self.create_streams(framesize=kwargs['framesize'])]
