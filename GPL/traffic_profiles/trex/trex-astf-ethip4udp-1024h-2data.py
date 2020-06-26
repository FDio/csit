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

Traffic profile: TODO: update !
 - Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
 - Packet: ETH / IP /
 - Direction 0 --> 1:
   - Destination MAC address: 52:54:00:00:nf_id:01
   - Source IP address range:      10.10.10.1 - 10.10.10.254
   - Destination IP address range: 20.20.20.1
 - Direction 1 --> 0:
   - Destination MAC address: 52:54:00:00:nf_id:02
   - Source IP address range:      20.20.20.1 - 20.20.20.254
   - Destination IP address range: 10.10.10.1
"""

from trex.astf.api import *

from profile_trex_astf_base_class import TrafficProfileBaseClass


class TrafficProfile(TrafficProfileBaseClass):
    """Traffic profile."""

    def __init__(self, **kwargs):
        """Initialization and setting of profile parameters."""

        super(TrafficProfileBaseClass, self).__init__()

        # IPs used in packet headers.
        self.p1_src_start_ip = u"192.168.0.0"
        self.p1_src_end_ip = u"192.168.3.255"
        self.p1_dst_start_ip = u"20.0.0.0"
        self.p1_dst_end_ip = u"20.0.3.255"

        self.udp_req = u"GET"
        self.udp_res = u"ACK"
        self.udp_fin = u"FIN"
        self.udp_data = u""

        self.headers_size = 42  # 14B l2 + 20B ipv4 + 8B udp

        self.delay = 8000000

    def define_profile(self):
        """Define profile to be used by advanced stateful traffic generator.

        This method MUST return:

            return ip_gen, templates, None

        :returns: IP generator and profile templates for ASTFProfile().
        :rtype: tuple
        """
        # client commands
        self.udp_req += self._gen_padding(self.headers_size + len(self.udp_req))
        self.udp_res += self._gen_padding(self.headers_size + len(self.udp_res))
        self.udp_data += self._gen_padding(self.headers_size, 1518)
        self.udp_fin += self._gen_padding(self.headers_size + len(self.udp_fin))
        prog_c = ASTFProgram(stream=False)
        prog_c.set_keepalive_msg(20000)
        prog_c.send_msg(self.udp_req)  # size and fill not supported in v2.73
        prog_c.recv_msg(1)

        prog_c.delay(self.delay)

        prog_c.send_msg(self.udp_data)
        prog_c.recv_msg(1)
        prog_c.send_msg(self.udp_data)
        prog_c.recv_msg(1)
        prog_c.send_msg(self.udp_fin)
        prog_c.recv_msg(1)

        # server commands
        prog_s = ASTFProgram(stream=False)
        prog_s.set_keepalive_msg(20000)
        prog_s.recv_msg(1)
        prog_s.send_msg(self.udp_res)

        prog_s.delay(self.delay)

        prog_s.send_msg(self.udp_data)
        prog_s.recv_msg(1)
        prog_s.send_msg(self.udp_data)
        prog_s.recv_msg(1)
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
            limit=64512,
            port=8080)
        temp_s = ASTFTCPServerTemplate(program=prog_s, assoc=s_assoc)  # TODO: default association ?
        template = ASTFTemplate(client_template=temp_c, server_template=temp_s)

        return ip_gen, template, None


        # TODO: packet size ?


def register():
    """Register this traffic profile to T-Rex.

    Do not change this function.

    :return: Traffic Profiles.
    :rtype: Object
    """
    return TrafficProfile()
