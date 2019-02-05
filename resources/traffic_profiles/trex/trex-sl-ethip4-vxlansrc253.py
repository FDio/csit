# Copyright (c) 2019 Cisco and/or its affiliates.
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
 - Packet: ETH / IP / VXLAN / ETH / IP
 - Direction 0 --> 1:
   - Source IP address:                172.17.0.2
   - Destination IP address:           172.16.0.1
   - VXLAN VNI:                        24
   - Payload source MAC address:       00:de:ad:00:00:00
   - Payload source IP address:        10.0.0.2
   - Payload destination MAC address:  00:de:ad:00:00:01
   - Payload destination IP address:   10.0.0.1
 - Direction 1 --> 0:
   - Source IP address:                172.27.0.2
   - Destination IP address:           172.26.0.1
   - VXLAN VNI:                        24
   - Payload source MAC address:       00:de:ad:00:00:01
   - Payload source IP address:        10.0.0.1
   - Payload destination MAC address:  00:de:ad:00:00:00
   - Payload destination IP address:   10.0.0.2

"""

from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass

# RFC 7348 - Virtual eXtensible Local Area Network (VXLAN):
# A Framework for Overlaying Virtualized Layer 2 Networks over Layer 3 Networks
# http://tools.ietf.org/html/rfc7348
_VXLAN_FLAGS = list('R'*24 + "RRRIRRRRR")


class VXLAN(Packet):
    name = "VXLAN"
    fields_desc = [FlagsField("flags", 0x08000000, 32, _VXLAN_FLAGS),
                   ThreeBytesField("vni", 0),
                   XByteField("reserved", 0x00)]

    def mysummary(self):
        return self.sprintf("VXLAN (vni=%VXLAN.vni%)")


bind_layers(UDP, VXLAN, dport=4789)
bind_layers(VXLAN, Ether)


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IP |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """

        # Direction 0 --> 1
        base_pkt_a = (
            Ether()/
            IP(src="172.17.0.2",dst="172.16.0.1")/
            UDP(sport=1337,dport=4789)/
            VXLAN(vni=24)/
            Ether(src="00:de:ad:00:00:00",dst="00:de:ad:00:00:01")/
            IP(src="10.0.0.2",dst="10.0.0.1"))

        # Direction 1 --> 0
        base_pkt_b = (
            Ether()/
            IP(src="172.27.0.2",dst="172.26.0.1")/
            UDP(sport=1337,dport=4789)/
            VXLAN(vni=24)/
            Ether(src="00:de:ad:00:00:01",dst="00:de:ad:00:00:00")/
            IP(src="10.0.0.1",dst="10.0.0.2"))


        # Direction 0 --> 1
        vm1 = STLScVmRaw([
            STLVmFlowVar(name="src", min_value="172.17.0.2" ,
                         max_value="172.17.0.254", size=4, op="inc"),
            STLVmFlowVar(name="src_mac", min_value=2 , max_value=3100,
                         size=2, op="inc"),
            STLVmWrFlowVar(fv_name="src", pkt_offset="IP.src"),
            STLVmWrFlowVar(fv_name="src_mac", pkt_offset=60),
            STLVmFixIpv4(offset = "IP")
        ])

        # Direction 1 --> 0
        vm2 = STLScVmRaw([
            STLVmFlowVar(name="src", min_value="172.27.0.2" ,
                         max_value="172.27.0.254", size=4, op="inc"),
            STLVmFlowVar(name="src_mac", min_value=2 , max_value=3100,
                         size=2, op="inc"),
            STLVmWrFlowVar(fv_name="src", pkt_offset="IP.src"),
            STLVmWrFlowVar(fv_name="src_mac", pkt_offset=60),
            STLVmFixIpv4(offset = "IP")
        ])

        # for now there's a single VXLAN tunnel per direction, the above
        # variations are for reference only
        vm1, vm2 = [], []

        return base_pkt_a, base_pkt_b, vm1, vm2

def register():
    """Register this traffic profile to T-rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()

