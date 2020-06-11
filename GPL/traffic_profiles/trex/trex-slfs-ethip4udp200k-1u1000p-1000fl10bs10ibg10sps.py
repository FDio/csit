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
Inspired by flowsim.
https://github.com/dmarion/vpp-toys/blob/master/trex/stl/flowsim.py

Stream profile:
 - 200 streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
 - Packet: ETH / IP / UDP
 - Direction 0 --> 1:
   - Source IP address range:      20.0.0.0 - 20.0.58.152
   - Destination IP address range: 12.0.0.2
   - UDP sport range:              1024 - 1036
   - UDP dport range:              1024 - 16023
 - Direction 1 --> 0:
   - Source IP address range:      12.0.0.2
   - Destination IP address range: 200.0.0.0
   - UDP sport range:              1024 - 1036
   - UDP dport range:              1024 - 16023
"""
import ipaddress
from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass

class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        # IPs used in packet headers.
        self.p1_src_start_ip = u"192.168.0.0"
        self.p1_src_end_ip = u"192.168.63.255"
        self.p1_dst_start_ip = u"20.0.0.0"
        self.p1_dst_end_ip = u"20.0.0.0"

        self.p2_src_start_ip = u"20.0.0.0"
        self.p2_src_end_ip = u"20.0.0.0"
        self.p2_dst_start_ip = u"68.142.68.0"
        self.p2_dst_end_ip = u"68.142.68.15"

        # UDP ports used in packet headers.
        self.p1_src_start_udp_port = 1024
        self.p1_src_end_udp_port = 1086
        self.p1_dst_start_udp_port = 1024
        self.p1_dst_end_udp_port = 1024

        self.p2_src_start_udp_port = 1024
        self.p2_src_end_udp_port = 1024
        self.p2_dst_start_udp_port = 1024
        self.p2_dst_end_udp_port = 65535

        # IPs used in packet headers.
        #self.p1_src_start_ip = u"10.10.10.2"
        #self.p1_src_end_ip = u"10.10.10.254"
        #self.p1_dst_start_ip = u"20.20.20.2"

        #self.p2_src_start_ip = u"20.20.20.2"
        #self.p2_src_end_ip = u"20.20.20.254"
        #self.p2_dst_start_ip = u"10.10.10.2"

        self.n_flows = 1032192
        self.n_ports_per_ip = 63
        self.n_streams = 128
        self.full_cycle = 64
        self.duty_cycle = 0.5

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IP |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """
        base_pkt_a = list()
        base_pkt_b = list()
        vm1 = list()
        vm2 = list()

        self.n_flows_per_stream = int(self.n_flows / self.n_streams)
        self.n_src_ips_per_stream = self.n_flows / self.n_streams / \
            self.n_ports_per_ip

        for stream in range(self.n_streams):

            # Direction 0 --> 1
            base_pkt_a_item = (
                Ether() /
                IP(
                    src=str(ipaddress.ip_address(self.p1_src_start_ip) + \
                        int(stream * self.n_src_ips_per_stream)),
                    dst=self.p1_dst_start_ip
                ) /
                UDP(
                    sport=self.p1_src_start_udp_port,
                    dport=self.p1_dst_start_udp_port
                )
            )
            base_pkt_a.append(base_pkt_a_item)

            # Direction 1 --> 0
            base_pkt_b_item = (
                Ether() /
                IP(
                    src=self.p2_src_start_ip,
                    dst=self.p2_dst_start_ip
                ) /
                UDP(
                    sport=self.p2_src_start_udp_port,
                    dport=self.p2_dst_start_udp_port + \
                        int(stream * self.n_flows_per_stream % \
                        (self.p2_dst_end_udp_port - self.p2_dst_start_udp_port \
                        + 1))
                )
            )
            base_pkt_b.append(base_pkt_b_item)

            # Direction 0 --> 1
            vm1_item = STLVM()
            vm1_item.var(name="sIP",
                    min_value=str(ipaddress.ip_address(self.p1_src_start_ip) \
                        + int(stream * self.n_src_ips_per_stream)),
                    max_value=str(ipaddress.ip_address(self.p1_src_start_ip) \
                        + int((stream * self.n_src_ips_per_stream) + \
                        self.n_src_ips_per_stream - 1)),
                    size=4,
                    op="inc")
            vm1_item.var(name="sport",
                    min_value=self.p1_src_start_udp_port,
                    max_value=self.p1_src_end_udp_port,
                    size=2,
                    op="inc",
                    next_var="sIP")
            vm1_item.var(name="dIP",
                    min_value=self.p1_dst_start_ip,
                    max_value=self.p1_dst_end_ip,
                    size=4,
                    op="inc")
            vm1_item.var(name="dport",
                    min_value=self.p1_dst_start_udp_port,
                    max_value=self.p1_dst_end_udp_port,
                    size=2,
                    op="inc")
            vm1_item.write(fv_name="sIP", pkt_offset="IP.src")
            vm1_item.write(fv_name="sport", pkt_offset="UDP.sport")
            vm1_item.write(fv_name="dIP", pkt_offset="IP.dst")
            vm1_item.write(fv_name="dport", pkt_offset="UDP.dport")
            vm1_item.fix_chksum(offset='IP')
            vm1.append(vm1_item)
            # Direction 0 --> 1
            vm2_item = STLVM()
            vm2_item.var(name="sIP",
                    min_value=self.p2_src_start_ip,
                    max_value=self.p2_src_end_ip,
                    size=4,
                    op="inc")
            vm2_item.var(name="sport",
                    min_value=self.p2_src_start_udp_port,
                    max_value=self.p2_src_end_udp_port,
                    size=2,
                    op="inc")
            vm2_item.var(name="dIP",
                    min_value=self.p2_dst_start_ip,
                    max_value=self.p2_dst_end_ip,
                    size=4,
                    op="inc")
            vm2_item.var(name="dport",
                    min_value=self.p2_dst_start_udp_port + \
                        int(stream * self.n_flows_per_stream % \
                        (self.p2_dst_end_udp_port - self.p2_dst_start_udp_port \
                        + 1)),
                    max_value=self.p2_dst_start_udp_port + \
                        int(((stream * self.n_flows_per_stream) + \
                        self.n_flows_per_stream - 1) % \
                        (self.p2_dst_end_udp_port - self.p2_dst_start_udp_port \
                        + 1)),
                    size=2,
                    op="inc",
                    next_var="dIP")
            vm2_item.write(fv_name="sIP", pkt_offset="IP.src")
            vm2_item.write(fv_name="sport", pkt_offset="UDP.sport")
            vm2_item.write(fv_name="dIP", pkt_offset="IP.dst")
            vm2_item.write(fv_name="dport", pkt_offset="UDP.dport")
            vm2_item.fix_chksum(offset='IP')
            vm2.append(vm2_item)

        return base_pkt_a, base_pkt_b, vm1, vm2

    def create_streams(self):
        """Create traffic streams.

        Implement your own traffic streams.

        :returns: Traffic streams.
        :rtype: list
        """
        base_pkt_a, base_pkt_b, vm1, vm2 = self.define_packets()

        # In most cases you will not have to change the code below:

        # Frame size is defined as an integer, e.g. 64, 1518:
        if isinstance(self.framesize, int):
            stream1 = list()
            stream2 = list()

            self.flows_per_second = self.n_flows / self.full_cycle
            self.streams_per_second = \
                self.flows_per_second / self.n_flows_per_stream
            self.burst_sec = self.full_cycle * self.duty_cycle
            self.inter_burst_gap = self.full_cycle - self.burst_sec
            #self.pps = int(self.rate[:-3]) * self.n_flows
            self.pps = int(self.rate[:-3])
            self.pps_per_stream = int(self.pps / \
                (self.n_streams * self.duty_cycle))
            self.pkts_per_burst = int((self.burst_sec * self.pps) / \
                (self.n_streams * self.duty_cycle))

            self.mode = STLTXMultiBurst(pps=self.pps_per_stream,
                                        pkts_per_burst=self.pkts_per_burst,
                                        ibg=self.inter_burst_gap * 1e6,
                                        count=2
                                       )
            print("pps_per_stream:", self.pps_per_stream)
            print("pps:", self.pps)
            print("streams_per_second:", self.streams_per_second)
            print("pkts_per_burst:", self.pkts_per_burst)
            print("flows_per_second:", self.flows_per_second)
            print("burst_sec:", self.burst_sec)
            print("inter_burst_gap:", self.inter_burst_gap)

            for i in range(self.n_streams):
                payload_len = max(0, self.framesize - len(base_pkt_a[i]) - 4)
                pkt_a = STLPktBuilder(
                    pkt=base_pkt_a[i]/self._gen_payload(payload_len), vm=vm1[i])
                stream1.append(STLStream(
                        isg=i*(1e6/self.streams_per_second),
                        packet=pkt_a,
                        mode=self.mode
                    )
                )
            for i in range(self.n_streams):
                payload_len = max(0, self.framesize - len(base_pkt_b[i]) - 4)
                pkt_b = STLPktBuilder(
                    pkt=base_pkt_b[i]/self._gen_payload(payload_len), vm=vm2[i])
                stream2.append(STLStream(
                        isg=1000+(i*(1e6/self.streams_per_second)),
                        packet=pkt_b,
                        mode=self.mode
                    )
                )
            # Packets for latency measurement:
            # Direction 0 --> 1
            pkt_lat_a = STLPktBuilder(
                pkt=base_pkt_a[0] / self._gen_payload(payload_len), vm=vm1[0]
            )
            # Direction 1 --> 0
            pkt_lat_b = STLPktBuilder(
                pkt=base_pkt_b[0] / self._gen_payload(payload_len), vm=vm2[0]
            )
            # Streams for latency measurement:
            # Direction 0 --> 1
            lat_stream1 = list()
            lat_stream1.append(STLStream(
                    packet=pkt_lat_a,
                    flow_stats=STLFlowLatencyStats(pg_id=0),
                    mode=STLTXCont(pps=9000)
                )
            )
            # Direction 1 --> 0
            # second traffic stream with a phase of 10ns (inter-stream gap)
            lat_stream2 = list()
            lat_stream2.append(STLStream(
                    packet=pkt_lat_b,
                    isg=10.0,
                    flow_stats=STLFlowLatencyStats(pg_id=1),
                    mode=STLTXCont(pps=9000)
                )
            )
            streams = list()
            streams.extend(stream1)
            streams.extend(stream2)
            streams.extend(lat_stream1)
            streams.extend(lat_stream2)
            return streams

def register():
    """Register this traffic profile to T-rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
