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
