# Copyright (c) 2023 Cisco and/or its affiliates.
#
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
#
# Licensed under the Apache License 2.0 or
# GNU General Public License v2.0 or later;  you may not use this file
# except in compliance with one of these Licenses. You
# may obtain a copy of the Licenses at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
#
# Note: If this file is linked with Scapy, which is GPLv2+, your use of it
# must be under GPLv2+.  If at any point in the future it is no longer linked
# with Scapy (or other GPLv2+ licensed software), you are free to choose
# Apache 2.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Stream profile for T-rex traffic generator.

Stream profile:
 - Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
 - Packet: ETH / DOT1Q / IP / VXLAN / ETH / IP
 - Direction 0 --> 1:
   - VLAN range:                       100
   - Source IP address:                172.17.[0..5].2
   - Destination IP address:           172.16.0.1
   - Source UDP port:                  random([1024..65535])
   - Destination UDP port:             4789
   - VXLAN VNI:                        [0..5]
   - Payload source MAC address:       00:aa:aa:00:00:[00..ff]
   - Payload source IP address:        10.0.[0..255].2
   - Payload destination MAC address:  00:bb:bb:00:00:[00..ff]
   - Payload destination IP address:   10.0.[0..255].1
 - Direction 1 --> 0:
   - VLAN range:                       200
   - Source IP address:                172.27.[0..5].2
   - Destination IP address:           172.26.0.1
   - Source UDP port:                  random([1024..65535])
   - Destination UDP port:             4789
   - VXLAN VNI:                        [0..5]
   - Payload source MAC address:       00:bb:bb:00:00:[00..ff]
   - Payload source IP address:        10.0.[0..255].1
   - Payload destination MAC address:  00:aa:aa:00:00:[00..ff]
   - Payload destination IP address:   10.0.[0..255].2
"""

from trex.stl.api import *
from profile_trex_stateless_base_class import TrafficStreamsBaseClass

# RFC 7348 - Virtual eXtensible Local Area Network (VXLAN):
# A Framework for Overlaying Virtualized Layer 2 Networks over Layer 3 Networks
# http://tools.ietf.org/html/rfc7348
_VXLAN_FLAGS = list("R" * 24 + "RRRIRRRRR")


class VXLAN(Packet):
    name = "VXLAN"
    fields_desc = [
        FlagsField("flags", 0x08000000, 32, _VXLAN_FLAGS),
        ThreeBytesField("vni", 0),
        XByteField("reserved", 0x00),
    ]

    def mysummary(self):
        return self.sprintf("VXLAN (vni=%VXLAN.vni%)")


bind_layers(UDP, VXLAN, dport=4789)
bind_layers(VXLAN, Ether)


class TrafficStreams(TrafficStreamsBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsBaseClass, self).__init__()

        self.nf_chains = 6

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | DOT1Q | IP | VXLAN | ETH | IP

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """

        # Direction 0 --> 1
        base_pkt_a = (
            Ether()
            / Dot1Q(vlan=100)
            / IP(src="172.17.0.2", dst="172.16.0.1")
            / UDP(sport=1024, dport=4789)
            / VXLAN(vni=0)
            / Ether(src="00:aa:aa:00:00:00", dst="00:bb:bb:00:00:00")
            / IP(src="10.0.0.2", dst="10.0.0.1", proto=61)
        )

        # Direction 1 --> 0
        base_pkt_b = (
            Ether()
            / Dot1Q(vlan=200)
            / IP(src="172.27.0.2", dst="172.26.0.1")
            / UDP(sport=1024, dport=4789)
            / VXLAN(vni=0)
            / Ether(src="00:bb:bb:00:00:00", dst="00:aa:aa:00:00:00")
            / IP(src="10.0.0.1", dst="10.0.0.2", proto=61)
        )

        # Direction 0 --> 1
        vm1 = STLScVmRaw(
            [
                STLVmFlowVar(
                    name="nf_id",
                    size=1,
                    op="inc",
                    min_value=0,
                    max_value=self.nf_chains - 1,
                ),
                STLVmFlowVar(
                    name="in_mac", size=2, op="inc", min_value=0, max_value=255
                ),
                STLVmFlowVar(
                    name="in_ip", size=1, op="inc", min_value=0, max_value=255
                ),
                STLVmFlowVar(
                    name="src_port",
                    size=2,
                    op="random",
                    min_value=1024,
                    max_value=65535,
                ),
                STLVmWrFlowVar(fv_name="nf_id", pkt_offset=32),
                STLVmWrFlowVar(fv_name="src_port", pkt_offset="UDP.sport"),
                STLVmWrFlowVar(fv_name="nf_id", pkt_offset=52),
                STLVmWrFlowVar(fv_name="in_mac", pkt_offset=58),
                STLVmWrFlowVar(fv_name="in_mac", pkt_offset=64),
                STLVmWrFlowVar(fv_name="in_ip", pkt_offset=82),
                STLVmWrFlowVar(fv_name="in_ip", pkt_offset=86),
                STLVmFixChecksumHw(
                    l3_offset="IP:{}".format(0),
                    l4_offset="UDP:{}".format(0),
                    l4_type=CTRexVmInsFixHwCs.L4_TYPE_UDP,
                ),
            ]
        )

        # Direction 1 --> 0
        vm2 = STLScVmRaw(
            [
                STLVmFlowVar(
                    name="nf_id",
                    size=1,
                    op="inc",
                    min_value=0,
                    max_value=self.nf_chains - 1,
                ),
                STLVmFlowVar(
                    name="in_mac", size=2, op="inc", min_value=0, max_value=255
                ),
                STLVmFlowVar(
                    name="in_ip", size=1, op="inc", min_value=0, max_value=255
                ),
                STLVmFlowVar(
                    name="src_port",
                    size=2,
                    op="random",
                    min_value=1024,
                    max_value=65535,
                ),
                STLVmWrFlowVar(fv_name="nf_id", pkt_offset=32),
                STLVmWrFlowVar(fv_name="src_port", pkt_offset="UDP.sport"),
                STLVmWrFlowVar(fv_name="nf_id", pkt_offset=52),
                STLVmWrFlowVar(fv_name="in_mac", pkt_offset=58),
                STLVmWrFlowVar(fv_name="in_mac", pkt_offset=64),
                STLVmWrFlowVar(fv_name="in_ip", pkt_offset=82),
                STLVmWrFlowVar(fv_name="in_ip", pkt_offset=86),
                STLVmFixChecksumHw(
                    l3_offset="IP:{}".format(0),
                    l4_offset="UDP:{}".format(0),
                    l4_type=CTRexVmInsFixHwCs.L4_TYPE_UDP,
                ),
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
