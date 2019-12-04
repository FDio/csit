# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.

from scapy.fields import BitField, XByteField, X3BytesField
from scapy.packet import Packet, bind_layers
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP


class VXLAN(Packet):
    name = "VXLAN"
    fields_desc = [BitField("flags", 0x08000000, 32),
                   X3BytesField("vni", 0),
                   XByteField("reserved", 0x00)]

    def mysummary(self):
        return self.sprintf("VXLAN (vni=%VXLAN.vni%)")

bind_layers(UDP, VXLAN, dport=4789)
bind_layers(VXLAN, Ether)
