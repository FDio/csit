# Copyright (c) 2020 Cisco and/or its affiliates.
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

from scapy.fields import BitField, XByteField, X3BytesField
from scapy.layers.inet import UDP
from scapy.layers.l2 import Ether
from scapy.packet import Packet, bind_layers


class VXLAN(Packet):
    name = u"VXLAN"
    fields_desc = [
        BitField(u"flags", 0x08000000, 32),
        X3BytesField(u"vni", 0),
        XByteField(u"reserved", 0x00)
    ]

    def mysummary(self):
        return self.sprintf(f"VXLAN (vni={VXLAN.vni})")


bind_layers(UDP, VXLAN, dport=4789)
bind_layers(VXLAN, Ether)
