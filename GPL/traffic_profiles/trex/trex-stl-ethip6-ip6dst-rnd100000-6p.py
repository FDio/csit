# Copyright (c) 2024 Cisco and/or its affiliates.
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
 - Three parallel bi-directional streams sent as W --> E and E --> W
   at the same time.
 - Packet: ETH / IPv6 /
"""

from trex.stl.api import *
from profile_trex_stateless_scale_class import TrafficStreamsScaleClass


class TrafficStreams(TrafficStreamsScaleClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsScaleClass, self).__init__()

        self.pkt_data = [
            # Direction W --> E:
            {
                "src_start_ip": "2100::1",
                "dst_start_ip": "2200::0",
                "dst_end_ip": "2200::1:869F",
                "seed": 1,
            },
            # Direction W --> E:
            {
                "src_start_ip": "2300::1",
                "dst_start_ip": "2400::0",
                "dst_end_ip": "2400::1:869F",
                "seed": 3,
            },
            # Direction W --> E:
            {
                "src_start_ip": "2500::1",
                "dst_start_ip": "2600::0",
                "dst_end_ip": "2600::1:869F",
                "seed": 5,
            },
            # Direction E --> W:
            {
                "src_start_ip": "2200::1",
                "dst_start_ip": "2100::0",
                "dst_end_ip": "2100::1:869F",
                "seed": 2,
            },
            # Direction E --> W:
            {
                "src_start_ip": "2400::1",
                "dst_start_ip": "2300::0",
                "dst_end_ip": "2300::1:869F",
                "seed": 4,
            },
            # Direction E --> W:
            {
                "src_start_ip": "2600::1",
                "dst_start_ip": "2500::0",
                "dst_end_ip": "2500::1:869F",
                "seed": 6,
            },
        ]
        self.pkt_base = []
        self.pkt_vm = []

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        Packet definition: | ETH | IPv6 |

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """
        for i in range(len(self.pkt_data)):
            base, count = self._get_start_end_ipv6(
                self.pkt_data[i]["dst_start_ip"], self.pkt_data[i]["dst_end_ip"]
            )

            self.pkt_base.append(
                Ether()
                / IPv6(
                    src=self.pkt_data[i]["src_start_ip"],
                    dst=self.pkt_data[i]["dst_start_ip"],
                )
            )
            self.pkt_vm.append(
                STLScVmRaw(
                    [
                        STLVmFlowVarRepeatableRandom(
                            name="ipv6_dst",
                            min_value=base,
                            max_value=base + count,
                            size=8,
                            seed=self.pkt_data[i]["seed"],
                            limit=(2**24 - 1),
                        ),
                        STLVmWrFlowVar(
                            fv_name="ipv6_dst",
                            pkt_offset="IPv6.dst",
                            offset_fixup=8,
                        ),
                    ]
                )
            )

        return self.pkt_base, self.pkt_vm


def register():
    """Register this traffic profile to T-rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
