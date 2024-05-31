# Copyright (c) 2021 Cisco and/or its affiliates.
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

import socket
import struct

from random import choice
from string import ascii_letters

from trex.stl.api import *


class TrafficStreamsBaseClass:
    """Base class for stream profiles for T-rex traffic generator."""

    STREAM_TABLE = {
        "IMIX_v4": [
            {"size": 60, "pps": 28, "isg": 0},
            {"size": 590, "pps": 20, "isg": 0.1},
            {"size": 1514, "pps": 4, "isg": 0.2},
        ],
        "IMIX_v4_1": [
            {"size": 64, "pps": 28, "isg": 0},
            {"size": 570, "pps": 16, "isg": 0.1},
            {"size": 1518, "pps": 4, "isg": 0.2},
        ],
    }

    def __init__(self):
        # Default value of frame size, it will be overwritten by the value of
        # "framesize" parameter of "get_streams" method.
        self.framesize = 64

        # If needed, add your own parameters.

    def _gen_payload(self, length):
        """Generate payload.

        If needed, implement your own algorithm.

        :param length: Length of generated payload.
        :type length: int
        :returns: The generated payload.
        :rtype: str
        """
        payload = ""
        for _ in range(length):
            payload += choice(ascii_letters)

        return payload

    def _get_start_end_ipv6(self, start_ip, end_ip):
        """Get start host and number of hosts from IPv6 as integer.

        :param start_ip: Start IPv6.
        :param end_ip: End IPv6.
        :type start_ip: string
        :type end_ip: string
        :return: Start host, number of hosts.
        :rtype tuple of int
        :raises: ValueError if start_ip is greater then end_ip.
        :raises: socket.error if the IP addresses are not valid IPv6 addresses.
        """
        try:
            ip1 = socket.inet_pton(socket.AF_INET6, start_ip)
            ip2 = socket.inet_pton(socket.AF_INET6, end_ip)

            hi1, lo1 = struct.unpack("!QQ", ip1)
            hi2, lo2 = struct.unpack("!QQ", ip2)

            if ((hi1 << 64) | lo1) > ((hi2 << 64) | lo2):
                raise ValueError("IPv6: start_ip is greater then end_ip")

            return lo1, abs(int(lo1) - int(lo2))

        except socket.error as err:
            print(err)
            raise

    def define_packets(self):
        """Define the packets to be sent from the traffic generator.

        This method MUST return:

            return base_pkt_a, base_pkt_b, vm1, vm2

            vm1 and vm2 CAN be None.

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
        base_pkt_a, base_pkt_b, vm1, vm2 = self.define_packets()

        # In most cases you will not have to change the code below:

        # Frame size is defined as an integer, e.g. 64, 1518:
        if isinstance(self.framesize, int):
            # Create a base packet and pad it to size; deduct FCS
            payload_len_a = max(0, self.framesize - len(base_pkt_a) - 4)
            payload_len_b = max(0, self.framesize - len(base_pkt_b) - 4)

            # Direction 0 --> 1
            pkt_a = STLPktBuilder(
                pkt=base_pkt_a / self._gen_payload(payload_len_a), vm=vm1
            )
            # Direction 1 --> 0
            pkt_b = STLPktBuilder(
                pkt=base_pkt_b / self._gen_payload(payload_len_b), vm=vm2
            )

            # Packets for latency measurement:
            # Direction 0 --> 1
            pkt_lat_a = STLPktBuilder(
                pkt=base_pkt_a / self._gen_payload(payload_len_a), vm=vm1
            )
            # Direction 1 --> 0
            pkt_lat_b = STLPktBuilder(
                pkt=base_pkt_b / self._gen_payload(payload_len_b), vm=vm2
            )

            # Create the streams:
            # Direction 0 --> 1
            stream1 = STLStream(packet=pkt_a, mode=STLTXCont(pps=9000))
            # Direction 1 --> 0
            # second traffic stream with a phase of 10ns (inter-stream gap)
            stream2 = STLStream(
                packet=pkt_b, isg=10.0, mode=STLTXCont(pps=9000)
            )

            # Streams for latency measurement:
            # Direction 0 --> 1
            lat_stream1 = STLStream(
                packet=pkt_lat_a,
                flow_stats=STLFlowLatencyStats(pg_id=0),
                mode=STLTXCont(pps=9000),
            )
            # Direction 1 --> 0
            # second traffic stream with a phase of 10ns (inter-stream gap)
            lat_stream2 = STLStream(
                packet=pkt_lat_b,
                isg=10.0,
                flow_stats=STLFlowLatencyStats(pg_id=1),
                mode=STLTXCont(pps=9000),
            )

            return [stream1, stream2, lat_stream1, lat_stream2]

        # Frame size is defined as a string, e.g.IMIX_v4_1:
        elif isinstance(self.framesize, str):

            stream1 = list()
            stream2 = list()

            for stream in self.STREAM_TABLE[self.framesize]:
                payload_len_a = max(0, stream["size"] - len(base_pkt_a) - 4)
                payload_len_b = max(0, stream["size"] - len(base_pkt_b) - 4)
                # Create a base packet and pad it to size
                pkt_a = STLPktBuilder(
                    pkt=base_pkt_a / self._gen_payload(payload_len_a), vm=vm1
                )
                pkt_b = STLPktBuilder(
                    pkt=base_pkt_b / self._gen_payload(payload_len_b), vm=vm2
                )

                # Create the streams:
                stream1.append(
                    STLStream(
                        packet=pkt_a,
                        isg=stream["isg"],
                        mode=STLTXCont(pps=stream["pps"]),
                    )
                )
                stream2.append(
                    STLStream(
                        packet=pkt_b,
                        isg=stream["isg"],
                        mode=STLTXCont(pps=stream["pps"]),
                    )
                )
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
        self.framesize = kwargs["framesize"]
        self.rate = kwargs["rate"]

        return self.create_streams()
