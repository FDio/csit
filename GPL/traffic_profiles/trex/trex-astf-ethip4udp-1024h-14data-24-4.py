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

    def __init__(self, **kwargs):
        """Initialization and setting of profile parameters."""

        super(TrafficProfileBaseClass, self).__init__()

        # IPs used in packet headers.
        self.p1_src_start_ip = u"192.168.0.0"
        self.p1_src_end_ip = u"192.168.3.255"
        self.p1_dst_start_ip = u"20.0.0.0"
        self.p1_dst_end_ip = u"20.0.3.255"

        self.headers_size = 42  # 14B l2 + 20B ipv4 + 8B UDP

        self.udp_data = u""

        self.ndata = 24  # TODO: set via input parameter
        self.nburst = 14
        self.delay = 12000000  # delay 12s (12,000,000 usec)
        self.u_delay = 4  #inter packet delay 125usec
        self.limit = 64512

    def define_profile(self):
        """Define profile to be used by advanced stateful traffic generator.

        This method MUST return:

            return ip_gen, templates

        :returns: IP generator and profile templates for ASTFProfile().
        :rtype: tuple
        """
        if self.framesize == 64:
            self.udp_data += self._gen_padding(self.headers_size, 72)
        if self.framesize == 1518:
            self.udp_data += self._gen_padding(self.headers_size, 1514)

        # client commands
        prog_c = ASTFProgram(stream=False)
        prog_c.set_keepalive_msg(20000)
        prog_c.send_msg(self.udp_data)

        prog_c.delay(self.delay)

        prog_c.set_var(u"var11", self.nburst)
        prog_c.set_label(u"a1:")
        prog_c.set_var(u"var1", self.ndata)
        prog_c.set_label(u"a:")
        prog_c.send_msg(self.udp_data)
        #prog_c.delay(self.u_delay)
        prog_c.jmp_nz(u"var1", u"a:")
        prog_c.delay(self.u_delay)
        prog_c.jmp_nz(u"var11", u"a1:")

        prog_c.delay(self.delay)

        # server commands
        prog_s = ASTFProgram(stream=False)
        prog_s.set_keepalive_msg(20000)
        prog_s.send_msg(self.udp_data)

        prog_s.delay(self.delay)

        prog_s.set_var(u"var21", self.nburst)
        prog_s.set_label(u"b1:")
        prog_s.set_var(u"var2", self.ndata)
        prog_s.set_label(u"b:")
        prog_s.send_msg(self.udp_data)
        #prog_s.delay(self.u_delay)
        prog_s.jmp_nz(u"var2", u"b:")
        prog_s.delay(self.u_delay)
        prog_s.jmp_nz(u"var21", u"b1:")

        prog_s.delay(self.delay)

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
            limit=self.limit,
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
