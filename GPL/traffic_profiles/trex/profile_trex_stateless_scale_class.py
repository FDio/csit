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

"""Base class for stream profiles for T-rex traffic generator.
"""

import socket
import struct

from random import choice
from string import ascii_letters

from trex.stl.api import *


class TrafficStreamsScaleClass:
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
        pkts, vms = self.define_packets()

        # Frame size is defined as an integer, e.g. 64, 1518:
        if isinstance(self.framesize, int):
            pkt_streams = list()
            lat_streams = list()
            for i in range(len(pkts)):
                payload_len = max(0, self.framesize - len(pkts[i]) - 4)

                pkt = STLPktBuilder(
                    pkt=pkts[i] / self._gen_payload(payload_len), vm=vms[i]
                )
                pkt_lat = STLPktBuilder(
                    pkt=pkts[i] / self._gen_payload(payload_len), vm=vms[i]
                )
                pkt_streams.append(
                    STLStream(
                        packet=pkt,
                        isg=10.0 * (i // (len(pkts) // 2)),
                        mode=STLTXCont(pps=9000),
                    )
                )
                lat_streams.append(
                    STLStream(
                        packet=pkt_lat,
                        isg=10.0 * (i // (len(pkts) // 2)),
                        flow_stats=STLFlowLatencyStats(pg_id=i),
                        mode=STLTXCont(pps=9000),
                    )
                )

            streams = list()
            streams.extend(pkt_streams)
            streams.extend(lat_streams)
            return streams

        # Frame size is defined as a string, e.g.IMIX_v4_1:
        elif isinstance(self.framesize, str):
            pkt_streams = list()
            for i in range(len(pkts)):
                for stream in self.STREAM_TABLE[self.framesize]:
                    payload_len = max(0, stream["size"] - len(pkts[i]) - 4)

                    pkt = STLPktBuilder(
                        pkt=pkts[i] / self._gen_payload(payload_len), vm=vms[i]
                    )
                    pkt_streams.append(
                        STLStream(
                            packet=pkt,
                            isg=stream["isg"],
                            mode=STLTXCont(pps=stream["pps"]),
                        )
                    )
            return pkt_streams

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
