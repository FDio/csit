# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""IPFIX utilities library. Provides classes that allow scapy to work
with IPFIX packets.

 Note:
 Template and data sets in one packet are not supported.
 Option template sets (Set_ID = 3) are not supported.
  """


from scapy.all import Packet, bind_layers
from scapy.fields import ByteField, ShortField, IntField, LongField, IPField,\
    StrFixedLenField, FieldListField
from scapy.layers.inet import UDP
from scapy.layers.inet6 import IP6Field
from scapy.contrib.ppi_geotag import UTCTimeField


class IPFIXHandler(object):
    """Class for handling IPFIX packets. To use, create instance of class before
     dissecting IPFIX packets with scapy, then run update_template every time
     an IPFIX template packet is received."""

    template_elements = {
        4: ByteField("Protocol_ID", 0x00),
        7: ShortField("src_port", 0),
        8: IPField("IPv4_src", ""),
        11: ShortField("dst_port", 0),
        12: IPField("IPv4_dst", ""),
        27: IP6Field("IPv6_src", "::"),
        28: IP6Field("IPv6_dst", "::"),
        86: LongField("packetTotalCount", 0),
        180: ShortField("udp_src_port", 0),
        181: ShortField("udp_dst_port", 0),
        182: ShortField("tcp_src_port", 0),
        183: ShortField("tcp_dst_port", 0),
        193: ByteField("Next_header", 0x00)
    }

    def __init__(self):
        """Initializer, registers IPFIX header and template layers with scapy.
        """
        bind_layers(UDP, IPFIXHeader, dport=4739)
        bind_layers(IPFIXHeader, IPFIXTemplate, Set_ID=2)

    def update_template(self, packet):
        """Updates IPFIXData class with new data template. Registers IPFIX data
        layer with scapy using the new template.

        :param packet: Packet containing an IPFIX template.
        :type packet: scapy.Ether
        """
        template_list = packet['IPFIX template'].Template
        template_id = packet['IPFIX template'].Template_ID

        IPFIXData.fields_desc = []
        for item in template_list[::2]:
            try:
                IPFIXData.fields_desc.append(self.template_elements[item])
            except KeyError:
                raise KeyError(
                    "Unknown IPFIX template element with ID {0}".format(item))
        bind_layers(IPFIXHeader, IPFIXData, Set_ID=template_id)
        # if the packet doesn't end here, assume it contains more data sets
        bind_layers(IPFIXData, IPFIXData)


class IPFIXHeader(Packet):
    """Class for IPFIX header."""
    name = "IPFIX header"
    fields_desc = [StrFixedLenField("Version", 0x000a, length=2),
                   ShortField("Message Length", 0),
                   UTCTimeField("Timestamp(UTC)", ""),
                   IntField("Sequence Number", 0),
                   IntField("Observation Domain ID", 0),
                   ShortField("Set_ID", 0),
                   ShortField("Set_Length", 0)
                   ]


class IPFIXTemplate(Packet):
    """Class for IPFIX template layer."""
    name = "IPFIX template"
    fields_desc = [ShortField("Template_ID", 256),
                   ShortField("nFields", 2),
                   FieldListField("Template", [], ShortField("type_len", ""),
                                  count_from=lambda p: p.nFields*2)
                   ]


class IPFIXData(Packet):
    """Class for IPFIX data layer. Needs to be updated with
    a template before use."""
    name = "IPFIX flow data"
    fields_desc = []
