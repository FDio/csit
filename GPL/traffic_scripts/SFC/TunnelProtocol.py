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

"""
This module implements the VxLAN/VXLAN-GPE/NSH protocol
for the packet analyse.
"""
from scapy.all import Packet
from scapy.all import XByteField, ShortField
from scapy.all import BitField, XBitField, IntField

class VxLAN(Packet):
    """Define the vxlan protocol for the packet analysis."""
    name = "vxlan"
    fields_desc = [XByteField("flags", 0x08), BitField("reserved", 0, 24),
                   BitField("vni", 0, 24), XByteField("reserved", 0x00)]

class VxLANGPE(Packet):
    """Define the vxlan-gpe protocol for the packet analysis."""
    name = "vxlan-gpe"
    fields_desc = [XByteField("flags", 0x0c), ShortField("reserved", 0),
                   XByteField("nextproto", 0x3), BitField("vni", 0, 24),
                   XByteField("reserved", 0x0)]

class NSH(Packet):
    """Define the NSH protocol for the packet analysis."""
    name = "nsh"
    fields_desc = [XBitField("Version", 0x0, 2), XBitField("OAM", 0x0, 1),
                   XBitField("Unassigned", 0x0, 1), XBitField("TTL", 0x0, 6),
                   XBitField("length", 0x6, 6), XBitField("Unassigned", 0x0, 4),
                   XBitField("MDtype", 0x1, 4), XByteField("nextproto", 0x3),
                   IntField("nsp_nsi", 0), IntField("c1", 0),
                   IntField("c2", 0), IntField("c3", 0), IntField("c4", 0)]
