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

"""Base class for profiles for T-rex advanced stateful (astf) traffic generator.
"""

from random import choices
from string import ascii_letters

from trex.astf.api import *


class TrafficProfileBaseClass:
    """Base class for profiles for T-rex astf traffic generator."""

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
        # Default values of required parameters; can be overwritten in
        # "get_profile" method.
        self.framesize = 64
        self._pcap_dir = u""

        # If needed, add your own parameters.

    @property
    def pcap_dir(self):
        """Pcap file directory.

        If needed, implement your own algorithm.

        :returns: Pcap file directory.
        :rtype: str
        """
        return self._pcap_dir

    def _gen_padding(self, current_length, required_length=0):
        """Generate padding.

        If needed, implement your own algorithm.

        :param current_length: Current length of the packet.
        :param required_length: Required length of the packet. If set to 0 then
        self.framesize value is used.
        :type current_length: int
        :type required_length: int
        :returns: The generated padding.
        :rtype: str
        """
        # TODO: Add support for IMIX frame size;
        #  use random.randrange(0, len(self.STREAM_TABLE[self.framesize])) ?
        if not required_length:
            required_length = self.framesize

        return str(choices(ascii_letters, k=required_length - current_length))

    def define_profile(self):
        """Define profile to be used by T-Rex astf traffic generator.

        This method MUST return:

            return ip_gen, templates, cap_list

            templates or cap_list CAN be None.

        :returns: IP generator and profile templates or list of pcap files for
        traffic generator.
        :rtype: tuple
        """
        raise NotImplementedError

    def create_profile(self):
        """Create traffic profile.

        Implement your own traffic profiles.

        :returns: Traffic profile.
        :rtype: trex.astf.trex_astf_profile.ASTFProfile
        """
        ip_gen, templates, cap_list = self.define_profile()

        # In most cases you will not have to change the code below:

        # profile
        profile = ASTFProfile(
            default_ip_gen=ip_gen,
            templates=templates,
            cap_list=cap_list
        )

        return profile

    def get_profile(self, **kwargs):
        """Get traffic profile created by "create_profile" method.

        If needed, add your own parameters.

        :param kwargs: Key-value pairs used by "create_profile" method while
        creating the profile.
        :returns: Traffic profile.
        :rtype: trex.astf.trex_astf_profile.ASTFProfile
        """
        self.framesize = kwargs[u"framesize"]
        self._pcap_dir = kwargs.get(
            u"pcap_dir",u"/opt/trex-core-2.88/scripts/avl"
        )

        return self.create_profile()
