# Copyright (c) 2022 Cisco and/or its affiliates.
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
 - Packet: ETH / IP / TCP
 - Direction 0 --> 1:
   - Source IP address range:      172.16.0.0 - 172.19.255.255
   - Destination IP address range: 20.16.0.0 - 20.19.255.255
 - Direction 1 --> 0:
   - Source IP address range:      destination IP address from packet received
     on port 1
   - Destination IP address range: source IP address from packet received
     on port 1

This is a profile for PPS tests, it combines TCP connect and data transfer.
No delays, server response waits for full request.
"""

from trex.astf.api import *
from profile_trex_astf_base_class import TrafficProfileBaseClass


class TrafficProfile(TrafficProfileBaseClass):
    """Traffic profile."""

    def define_profile(self):
        """Define profile to be used by advanced stateful traffic generator.

        This method MUST return:

            return ip_gen, templates, None

        :returns: IP generator and profile templates for ASTFProfile().
        :rtype: tuple
        """
        # IPs used in packet headers.
        p1_src_start_ip = "172.16.0.0"
        p1_src_end_ip = "172.19.255.255"
        p1_dst_start_ip = "20.16.0.0"
        p1_dst_end_ip = "20.19.255.255"

        # Headers length, not sure why TRex needs 32B for segment header.
        real_headers_size = 70  # 18B L2 + 20B IPv4 + 32B TCP.
        trex_headers_size = real_headers_size - 12  # As if TCP header is 20B.
        trex_mss = self.framesize - trex_headers_size
        real_mss = trex_mss - 12  # TRex honors segment header+data limit.
        data_size = self.n_data_frames * real_mss

        # client commands
        prog_c = ASTFProgram()
        prog_c.connect()
        prog_c.set_var("var1", self.n_data_frames)
        prog_c.set_label("a1:")
        prog_c.send("1" * real_mss)
        prog_c.recv(real_mss)
        prog_c.jmp_nz("var1", "a1:")

        # server commands
        prog_s = ASTFProgram()
        prog_s.accept()
        prog_s.set_var("var2", self.n_data_frames)
        prog_s.set_label("a2:")
        prog_s.recv(real_mss)
        prog_s.send("1" * real_mss)
        prog_s.jmp_nz("var2", "a2:")

        # ip generators
        ip_gen_c = ASTFIPGenDist(
            ip_range=[p1_src_start_ip, p1_src_end_ip],
            distribution="seq",
        )
        ip_gen_s = ASTFIPGenDist(
            ip_range=[p1_dst_start_ip, p1_dst_end_ip],
            distribution="seq",
        )
        ip_gen = ASTFIPGen(
            glob=ASTFIPGenGlobal(ip_offset="0.0.0.1"),
            dist_client=ip_gen_c,
            dist_server=ip_gen_s,
        )

        # server association
        s_assoc = ASTFAssociation(rules=ASTFAssociationRule(port=8080))

        # template
        temp_c = ASTFTCPClientTemplate(
            program=prog_c,
            ip_gen=ip_gen,
            limit=16515072,  # TODO: set via input parameter
            port=8080,
        )
        temp_s = ASTFTCPServerTemplate(program=prog_s, assoc=s_assoc)
        template = ASTFTemplate(client_template=temp_c, server_template=temp_s)

        globinfo = ASTFGlobalInfo()
        # Ensure correct data frame size.
        globinfo.tcp.mss = trex_mss
        globinfo.tcp.txbufsize = trex_mss
        globinfo.tcp.rxbufsize = trex_mss
        kwargs = dict(
            default_c_glob_info=globinfo,
            default_s_glob_info=globinfo,
        )

        return ip_gen, template, kwargs


def register():
    """Register this traffic profile to T-Rex.

    Do not change this function.

    :return: Traffic Profiles.
    :rtype: Object
    """
    return TrafficProfile()
