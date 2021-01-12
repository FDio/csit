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

This is a profile for PPS tests, it combines UDP connect and data transfer.
No delays, server response waits for full request.
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
        self.p1_src_end_ip = u"192.168.15.255"
        self.p1_dst_start_ip = u"20.0.0.0"
        self.p1_dst_end_ip = u"20.0.15.255"

        self.headers_size = 42  # 14B l2 + 20B ipv4 + 8B UDP

        self.udp_data = u""

        self.n_data = 32  # TODO: set via input parameter
        self.m_delay = 1200000  # delay 1200s (1,200,000 ms)
        self.u_delay = 1000 * self.m_delay  # delay 1200s (1,200,000,000 us)
        self.limit = 258048

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

        # Client program.
        prog_c = ASTFProgram(stream=False)
        prog_c.set_keepalive_msg(self.m_delay)
        prog_c.send_msg(self.udp_data)
        # No delay, PPS tests combine connect and data send (no data receive).
        prog_c.set_var(u"var1", self.n_data)
        prog_c.set_label(u"a:")
        prog_c.send_msg(self.udp_data)
        prog_c.jmp_nz(u"var1", u"a:")
        # We should read the server response,
        # but no reason to overload client workers even more.

        # Server program.
        prog_s = ASTFProgram(stream=False)
        prog_s.set_keepalive_msg(self.m_delay)
        # If server closes too soon, new instances are started
        # leading in too much replies. To prevent that, we need to recv all.
        prog_s.recv_msg(1 + self.n_data)
        # In packet loss scenarios, some instances never get here.
        # This maybe increases server traffic duration,
        # but no other way if we want to avoid
        # TRex creating a second instance of the same server.
        prog_s.send_msg(self.udp_data)
        prog_s.set_var(u"var2", self.n_data)
        prog_s.set_label(u"b:")
        prog_s.send_msg(self.udp_data)
        prog_s.jmp_nz(u"var2", u"b:")
        # VPP never duplicates packets,
        # so it is safe to close the server instance now.

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
