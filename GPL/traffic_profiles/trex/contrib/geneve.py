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
# with Scapy (or other GPLv2+ licensed software), you are free to choose Apache 2.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Geneve: Generic Network Virtualization Encapsulation.

Currently used TRex v2.82 uses scapy version 2.3.1 where the geneve layer
implementation is missing.
"""

from scapy.compat import bytes_hex, orb
from scapy.error import warning
from scapy.fields import BitField, XByteField, XShortEnumField, X3BytesField,\
    StrField
from scapy.layers.inet import IP, UDP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether, ETHER_TYPES
from scapy.packet import Packet, bind_layers


class XStrField(StrField):
    """
    StrField which value is printed as hexadecimal.
    """

    def i2repr(self, pkt, x):
        if x is None:
            return repr(x)
        return bytes_hex(x).decode()


class GENEVEOptionsField(XStrField):
    islist = 1

    def getfield(self, pkt, s):
        opln = pkt.optionlen * 4
        if opln < 0:
            warning("bad optionlen (%i). Assuming optionlen=0" % pkt.optionlen)
            opln = 0
        return s[opln:], self.m2i(pkt, s[:opln])


class GENEVE(Packet):
    name = "GENEVE"
    fields_desc = [BitField("version", 0, 2),
                   BitField("optionlen", None, 6),
                   BitField("oam", 0, 1),
                   BitField("critical", 0, 1),
                   BitField("reserved", 0, 6),
                   XShortEnumField("proto", 0x0000, ETHER_TYPES),
                   X3BytesField("vni", 0),
                   XByteField("reserved2", 0x00),
                   GENEVEOptionsField("options", "")]

    def post_build(self, p, pay):
        p += pay
        optionlen = self.optionlen
        if optionlen is None:
            optionlen = (len(self.options) + 3) // 4
            p = bytes([optionlen & 0x2f | orb(p[0]) & 0xc0]) + p[1:]
        return p

    def answers(self, other):
        if isinstance(other, GENEVE):
            if (self.proto == other.proto) and (self.vni == other.vni):
                return self.payload.answers(other.payload)
        else:
            return self.payload.answers(other)
        return 0

    def mysummary(self):
        return self.sprintf("GENEVE (vni=%GENEVE.vni%,"
                            "optionlen=%GENEVE.optionlen%,"
                            "proto=%GENEVE.proto%)")


bind_layers(UDP, GENEVE, dport=6081)
bind_layers(GENEVE, Ether, proto=0x6558)
bind_layers(GENEVE, IP, proto=0x0800)
bind_layers(GENEVE, IPv6, proto=0x86dd)
