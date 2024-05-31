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

    def define_profile(self):
        """Define profile to be used by advanced stateful traffic generator.

        This method MUST return:
            return ip_gen, templates, None

        :returns: IP generator and profile templates ASTFProfile().
        :rtype: tuple
        """
        # IPs used in packet headers.
        p1_src_start_ip = "192.168.0.0"
        p1_src_end_ip = "192.168.15.255"
        p1_dst_start_ip = "20.0.0.0"
        p1_dst_end_ip = "20.0.15.255"

        # Headers length
        headers_size = 46  # 18B L2 + 20B IPv4 + 8B UDP.

        # UDP messages, not padded yet.
        udp_req = "GET"
        udp_res = "ACK"

        # Padd to the required frame size.
        udp_req += self._gen_padding(headers_size + len(udp_req))
        udp_res += self._gen_padding(headers_size + len(udp_res))

        # No need to set keepalive, both programs end just after start&send.

        # client commands
        prog_c = ASTFProgram(stream=False)
        # send REQ message
        prog_c.send_msg(udp_req)
        # No need to process the response, seeing L2 counter is enough.
        # Client program can end here.

        # server commands
        prog_s = ASTFProgram(stream=False)
        # When server instance is created means REQ is visible in L2 counter.
        # No need to receive explicitly?
        # send RES message
        prog_s.send_msg(udp_res)
        # Server program can end here.

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
            limit=258048,  # TODO: set via input parameter ?
            port=8080,
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
