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

"""Traffic profile for T-rex advanced stateful (astf) traffic generator.

Traffic profile:
 - Two streams sent in directions 0 --> 1 (client -> server, requests) and
   1 --> 0 (server -> client, responses) at the same time.
 - Packet: ETH / IP / UDP
 - Direction 0 --> 1:
   - Source IP address range:      192.168.0.0 - 192.168.3.255
   - Destination IP address range: 20.0.0.0 - 20.0.3.255
 - Direction 1 --> 0:
   - Source IP address range:      destination IP address from packet received
     on port 1
   - Destination IP address range: source IP address from packet received
     on port 1
"""

from trex.astf.api import *

from profile_trex_astf_base_class import TrafficProfileBaseClass


class TrafficProfile(TrafficProfileBaseClass):
    """Traffic profile."""

    def __init__(self):
        """Initialization and setting of profile parameters."""

        super(TrafficProfileBaseClass, self).__init__()

        # IPs used in packet headers.
        self.p1_src_start_ip = u"192.168.0.0"
        self.p1_src_end_ip = u"192.168.3.255"
        self.p1_dst_start_ip = u"20.0.0.0"
        self.p1_dst_end_ip = u"20.0.3.255"

        # UDP messages
        self.udp_req = u"GET"
        self.udp_res = u"ACK"

        # Headers length
        self.headers_size = 42  # 14B l2 + 20B ipv4 + 8B udp

        # Required UDP keepalive value for T-Rex
        self.udp_keepalive = 2000  # 2s (2,000 msec)

    def define_profile(self):
        """Define profile to be used by advanced stateful traffic generator.

        This method MUST return:
            return ip_gen, templates, None

        :returns: IP generator and profile templates ASTFProfile().
        :rtype: tuple
        """
        # ip generators
        ip_gen_c = ASTFIPGenDist(
            ip_range=[self.p1_src_start_ip, self.p1_src_end_ip],
            distribution=u"seq"
        )
        ip_gen_s = ASTFIPGenDist(
            ip_range=[self.p1_dst_start_ip, self.p1_dst_end_ip],
            distribution=u"seq"
        )
        ip_gen = ASTFIPGen(
            glob=ASTFIPGenGlobal(ip_offset=u"0.0.0.1"),
            dist_client=ip_gen_c,
            dist_server=ip_gen_s
        )

        # server association
        s_assoc = ASTFAssociation(rules=ASTFAssociationRule(port=8080))

        # templates
        templates = list()
        streams = list()

        # Frame size is defined as an integer, e.g. 64, 1518:
        if isinstance(self.framesize, int):
            streams.append({u"size": self.framesize, u"cps": 1})
        # Frame size is defined as a string, e.g.IMIX_v4_1:
        elif isinstance(self.framesize, str):
            for stream in self.STREAM_TABLE[self.framesize]:
                streams.append(
                    {u"size": stream[u"size"], u"cps": stream[u"pps"]}
                )

        for stream in streams:
            self.udp_req += self._gen_padding(
                self.headers_size + len(self.udp_req), stream[u"size"]
            )
            self.udp_res += self._gen_padding(
                self.headers_size + len(self.udp_res), stream[u"size"]
            )

            # client commands
            prog_c = ASTFProgram(stream=False)
            # set the keepalive timer for UDP flows to not close udp session
            # immediately after packet exchange
            prog_c.set_keepalive_msg(self.udp_keepalive)
            # send REQ message
            prog_c.send_msg(self.udp_req)
            # receive RES message
            prog_c.recv_msg(1)
            prog_c.delay(self.udp_keepalive * 1000)  # delay is defined in usec

            # server commands
            prog_s = ASTFProgram(stream=False)
            # set the keepalive timer for UDP flows to not close udp session
            # immediately after packet exchange
            prog_c.set_keepalive_msg(self.udp_keepalive)
            # receive REQ message
            prog_s.recv_msg(1)
            # send RES message
            prog_s.send_msg(self.udp_res)
            prog_s.delay(self.udp_keepalive * 1000)  # delay is defined in usec

            # template
            temp_c = ASTFTCPClientTemplate(
                program=prog_c,
                ip_gen=ip_gen,
                port=8080,
                cps=stream[u"cps"],
                limit=64512,  # TODO: set via input parameter ?
            )
            temp_s = ASTFTCPServerTemplate(program=prog_s, assoc=s_assoc)
            templates.append(
                ASTFTemplate(client_template=temp_c, server_template=temp_s)
            )

        return ip_gen, templates, None


def register():
    """Register this traffic profile to T-Rex.

    Do not change this function.

    :return: Traffic Profiles.
    :rtype: Object
    """
    return TrafficProfile()
