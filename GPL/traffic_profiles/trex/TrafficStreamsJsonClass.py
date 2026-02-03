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

"""Base class for stream profiles for T-rex traffic generator.
"""

import json
import os

from trex.stl.api import *

CP = os.path.join(os.path.abspath(os.sep), "/opt/frouter-perf")


class TrafficStreamsJsonClass:
    """Base class for stream profiles for T-rex traffic generator."""

    def __init__(self):
        # Default value of frame size, it will be overwritten by the value of
        # "framesize" parameter of "get_streams" method.
        self.framesize = 64

    def define_packets(self):
        """Define the packets to be sent from the traffic generator.

        This method MUST return:

            return pkt, vm

        :returns: Packets to be sent from the traffic generator.
        :rtype: tuple
        """
        raise NotImplementedError

    def create_streams(self):
        """Create traffic streams.

        Implement your own traffic streams.

        :returns: Traffic streams.
        :rtype: list
        """
        pkt_streams = []
        lat_streams = []

        with open(os.path.join(CP, "packet-profile.json")) as packets_json:
            packets_data = json.load(packets_json)

        for profile in packets_data["profiles"]:
            for i, stream in enumerate(profile["streams"]):
                self.stream_data = stream
                pkt, vm = self.define_packets()
                packet = STLPktBuilder(pkt=pkt, vm=vm)
                pkt_streams.append(
                    STLStream(
                        packet=packet,
                        mode=STLTXCont(pps=9000)
                    )
                )
                lat_streams.append(
                    STLStream(
                        packet=packet,
                        flow_stats=STLFlowLatencyStats(pg_id=i),
                        mode=STLTXCont(pps=9000)
                    )
                )

        streams = []
        streams.extend(pkt_streams)
        streams.extend(lat_streams)
        return streams

    def get_streams(self, **kwargs):
        """Get traffic streams created by "create_streams" method.

        If needed, add your own parameters.

        :param kwargs: Key-value pairs used by "create_streams" method while
        creating streams.
        :returns: Traffic streams.
        :rtype: list
        """
        self.framesize = kwargs["framesize"]
        self.rate = kwargs["rate"]

        return self.create_streams()
