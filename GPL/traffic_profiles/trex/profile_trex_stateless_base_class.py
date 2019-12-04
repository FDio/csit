# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.

"""Base class for stream profiles for T-rex traffic generator.
"""

import sys
import socket
import struct

from random import choice
from string import ascii_letters

from trex.stl.api import *


class TrafficStreamsBaseClass:
    """Base class for stream profiles for T-rex traffic generator."""

    STREAM_TABLE = {
        u"IMIX_v4": [
            {u"size": 60, u"pps": 28, u"isg": 0},
            {u"size": 590, u"pps": 20, u"isg": 0.1},
            {u"size": 1514, u"pps": 4, u"isg": 0.2}
        ],
        'IMIX_v4_1': [
            {u"size": 64, u"pps": 28, u"isg": 0},
            {u"size": 570, u"pps": 16, u"isg": 0.1},
            {u"size": 1518, u"pps": 4, u"isg": 0.2}
        ]
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
        payload = u""
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

            hi1, lo1 = struct.unpack(u"!QQ", ip1)
            hi2, lo2 = struct.unpack(u"!QQ", ip2)

            if ((hi1 << 64) | lo1) > ((hi2 << 64) | lo2):
                raise ValueError(u"IPv6: start_ip is greater then end_ip")

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

            # Create a base packet and pad it to size
            payload_len = max(0, self.framesize - len(base_pkt_a) - 4)  # No FCS

            # Direction 0 --> 1
            pkt_a = STLPktBuilder(
                pkt=base_pkt_a / self._gen_payload(payload_len), vm=vm1
            )
            # Direction 1 --> 0
            pkt_b = STLPktBuilder(
                pkt=base_pkt_b / self._gen_payload(payload_len), vm=vm2
            )

            # Packets for latency measurement:
            # Direction 0 --> 1
            pkt_lat_a = STLPktBuilder(
                pkt=base_pkt_a / self._gen_payload(payload_len), vm=vm1
            )
            # Direction 1 --> 0
            pkt_lat_b = STLPktBuilder(
                pkt=base_pkt_b / self._gen_payload(payload_len), vm=vm2
            )

            # Create the streams:
            # Direction 0 --> 1
            stream1 = STLStream(packet=pkt_a, mode=STLTXCont(pps=9000))
            # Direction 1 --> 0
            # second traffic stream with a phase of 10ns (inter-stream gap)
            stream2 = STLStream(packet=pkt_b, isg=10.0,
                                mode=STLTXCont(pps=9000))

            # Streams for latency measurement:
            # Direction 0 --> 1
            lat_stream1 = STLStream(
                packet=pkt_lat_a, flow_stats=STLFlowLatencyStats(pg_id=0),
                mode=STLTXCont(pps=9000)
            )
            # Direction 1 --> 0
            # second traffic stream with a phase of 10ns (inter-stream gap)
            lat_stream2 = STLStream(
                packet=pkt_lat_b, isg=10.0,
                flow_stats=STLFlowLatencyStats(pg_id=1),
                mode=STLTXCont(pps=9000)
            )

            return [stream1, stream2, lat_stream1, lat_stream2]

        # Frame size is defined as a string, e.g.IMIX_v4_1:
        elif isinstance(self.framesize, str):

            stream1 = list()
            stream2 = list()

            for stream in self.STREAM_TABLE[self.framesize]:
                payload_len_a = max(0, stream[u"size"] - len(base_pkt_a) - 4)
                payload_len_b = max(0, stream[u"size"] - len(base_pkt_b) - 4)
                # Create a base packet and pad it to size
                pkt_a = STLPktBuilder(
                    pkt=base_pkt_a / self._gen_payload(payload_len_a),
                    vm=vm1)
                pkt_b = STLPktBuilder(
                    pkt=base_pkt_b / self._gen_payload(payload_len_b),
                    vm=vm2)

                # Create the streams:
                stream1.append(STLStream(
                    packet=pkt_a, isg=stream[u"isg"],
                    mode=STLTXCont(pps=stream[u"pps"]))
                )
                stream2.append(STLStream(
                    packet=pkt_b, isg=stream[u"isg"],
                    mode=STLTXCont(pps=stream[u"pps"]))
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
        self.framesize = kwargs[u"framesize"]

        return self.create_streams()
