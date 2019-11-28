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
