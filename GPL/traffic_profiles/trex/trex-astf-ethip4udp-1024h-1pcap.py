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


    def define_profile(self):
        """Define profile to be used by advanced stateful traffic generator.

        This method MUST return:

            return ip_gen, None, cap_list

        :returns: IP generator and profile templates for ASTFProfile().
        :rtype: tuple
        """
        # ip generator
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

        # pcap list
        pcap_dir = self._get_pcap_dir()
        cap_list = [
            ASTFCapInfo(
                file=f"{pcap_dir}/delay_10_http_get_0.pcap",
                cps=1,
                port=8080
            )
        ]

        return ip_gen, None, cap_list


def register():
    """Register this traffic profile to T-Rex.

    Do not change this function.

    :return: Traffic Profiles.
    :rtype: Object
    """
    return TrafficProfile()
