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
 - Packet: ETH / IP / TCP
 - Direction 0 --> 1:
   - Source IP address range:      192.168.0.0 - 192.168.15.255
   - Destination IP address range: 20.0.0.0 - 20.0.15.255
 - Direction 1 --> 0:
   - Source IP address range:      destination IP address from packet received
     on port 1
   - Destination IP address range: source IP address from packet received
     on port 1
"""

from trex.astf.api import *
from profile_trex_astf_base_class import TrafficProfileBaseClass


class TrafficProfile(TrafficProfileBaseClass):
    """Traffic profile.

    TCP traffic with data is transferred as several "payloads"
    in both directions. The payload in client->server direction is called
    "request" and the payload in server->client direction is called "response".
    In this profile, the data transfer is symmetric and both directions
    are independent (neither side is waiting for other side's payload).
    There are multiple payload being transferred, but the next payload
    starts transferring only after the previous payload has been acked,
    and after inter-payload delay. That delay acts as a poor man's rate limiter,
    chosing small enough payload size will prevent the TCP trasfer rate
    from increasing too much.

    The address ranges are hardcoded.
    The number of clients-server pairs (self.limit) is also hardcoded,
    as it has to fit the ranges.

    This template uses the default value cps=1, it is expected
    the profile launcher script changes it via multiplier.

    Other parameters are configurable via kwargs, they affect the single
    client-server pair:
    - framesize [B] - Target size for data frame, mss value is comuted from that.
        Note that is the payload size is not divisible by the packet's data size,
        the last packet will be smaller, which is fine.
    - payload_size [B] - How big a chunk of data to transfer before waiting for acks.
    - n_payloads [1] - How many chunks of data to transfer per client.
    - payload_delay [us] - How long to wait between payloads.
    - phase delay [us] - How long to wait after connect and before close.
    """

    def __init__(self, **kwargs):
        """Initialization and setting of profile parameters."""

        super(TrafficProfileBaseClass, self).__init__()

        # IPs used in packet headers.
        self.p1_src_start_ip = u"192.168.0.0"
        self.p1_src_end_ip = u"192.168.15.255"
        self.p1_dst_start_ip = u"20.0.0.0"
        self.p1_dst_end_ip = u"20.0.15.255"

        self.limit = 258048

        self.framesize = kwargs.get(u"framesize")
        self.payload_size = kwargs.get(u"payload_size")
        self.n_payloads = kwargs.get(u"n_payloads")
        self.payload_delay = kwargs.get(u"payload_delay")
        self.phase_delay = kwargs.get(u"phase_delay")

        if self.framesize == 64:
            self.mss = 18
        if self.framesize == 1518:
            self.mss = 1460

    def define_profile(self):
        """Define profile to be used by advanced stateful traffic generator.

        This method MUST return:

            return ip_gen, templates

        :returns: IP generator and profile templates for ASTFProfile().
        :rtype: tuple
        """
        # TODO: Does the header size affect any of this?
        tcp_data += self._gen_padding(0, self.payload_size)

        # client commands
        prog_c = ASTFProgram()
        prog_c.connect()  # syn

        prog_c.delay(self.phase_delay)

        prog_c.set_var(u"var1", self.n_payloads)
        prog_c.set_label(u"a:")
        prog_c.send(tcp_data)
        prog_c.delay(self.payload_delay)
        prog_c.jmp_nz(u"var1", u"a:")

        prog_c.delay(self.phase_delay)

        # server commands
        prog_s = ASTFProgram()
        prog_s.accept()  # syn-ack

        prog_s.delay(self.phase_delay)

        prog_s.set_var(u"var1", self.n_payloads)
        prog_s.set_label(u"a:")
        prog_s.send(tcp_data)
        prog_s.delay(self.payload_delay)
        prog_s.jmp_nz(u"var1", u"a:")

        # No need for phase delay as we are waiting anyway.
        prog_s.wait_for_peer_close()  # ack + fin-ack

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

        glob_info = ASTFGlobalInfoPerTemplate()
        glob_info.tcp.mss = self.mss

        # server association
        s_assoc = ASTFAssociation(rules=ASTFAssociationRule(port=8080))

        # template
        temp_c = ASTFTCPClientTemplate(
            program=prog_c,
            ip_gen=ip_gen,
            limit=self.limit,  # TODO: set via input parameter
            port=8080,
            glob_info=glob_info
        )
        temp_s = ASTFTCPServerTemplate(
            program=prog_s,
            assoc=s_assoc,
            glob_info=glob_info
        )
        template = ASTFTemplate(client_template=temp_c, server_template=temp_s)

        return ip_gen, template, None


def register():
    """Register this traffic profile to T-Rex.

    Do not change this function.

    :return: Traffic Profiles.
    :rtype: Object
    """
    return TrafficProfile()
