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
   - Source IP address range:      192.168.0.0 - 192.168.15.255
   - Destination IP address range: 20.0.0.0 - 20.0.15.255
 - Direction 1 --> 0:
   - Source IP address range:      destination IP address from packet received
     on port 1
   - Destination IP address range: source IP address from packet received
     on port 1

This is a profile for CPS tests, it only sets up UDP session.
No delays, no data transfer.
Keepalive mechanism cannot be disabled, so it is at least set to long waits.
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
        self.p1_src_end_ip = u"192.168.15.255"
        self.p1_dst_start_ip = u"20.0.0.0"
        self.p1_dst_end_ip = u"20.0.15.255"

        # UDP messages
        self.udp_req = u"GET"
        self.udp_res = u"ACK"

        # Headers length
        self.headers_size = 42  # 14B l2 + 20B ipv4 + 8B udp

        # Required UDP keepalive value for T-Rex
        self.udp_keepalive = 2000*1000*100  # 200000s (200,000,000 msec)

    def define_profile(self):
        """Define profile to be used by advanced stateful traffic generator.

        This method MUST return:
            return ip_gen, templates, None

        :returns: IP generator and profile templates ASTFProfile().
        :rtype: tuple
        """
        self.udp_req += self._gen_padding(self.headers_size + len(self.udp_req))
        self.udp_res += self._gen_padding(self.headers_size + len(self.udp_res))

        # client commands
        prog_c = ASTFProgram(stream=False)
        prog_c.set_keepalive_msg(self.udp_keepalive)
        # send REQ message
        prog_c.send_msg(self.udp_req)
        # receive RES message
        prog_c.recv_msg(1)

        # server commands
        prog_s = ASTFProgram(stream=False)
        prog_c.set_keepalive_msg(self.udp_keepalive)
        # receive REQ message
        prog_s.recv_msg(1)
        # send RES message
        prog_s.send_msg(self.udp_res)

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

        # template
        temp_c = ASTFTCPClientTemplate(
            program=prog_c,
            ip_gen=ip_gen,
            limit=258048,  # TODO: set via input parameter ?
            port=8080
        )
        temp_s = ASTFTCPServerTemplate(program=prog_s, assoc=s_assoc)
        template = ASTFTemplate(client_template=temp_c, server_template=temp_s)

        return ip_gen, template, None


def register():
    """Register this traffic profile to T-Rex.

    Do not change this function.

    :return: Traffic Profiles.
    :rtype: Object
    """
    return TrafficProfile()
