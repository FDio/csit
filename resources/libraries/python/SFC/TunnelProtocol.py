# Copyright (c) 2017 Cisco and/or its affiliates.
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
    fields_desc = [XBitField("flags", 0x0, 10), XBitField("length", 0x6, 6),
                   XByteField("MDtype", 0x1), XByteField("nextproto", 0x3),
                   IntField("nsp_nsi", 0), IntField("c1", 0),
                   IntField("c2", 0), IntField("c3", 0), IntField("c4", 0)]
