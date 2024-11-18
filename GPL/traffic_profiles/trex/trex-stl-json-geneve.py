# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""Stream profile for T-Rex traffic generator.

Stream profile:
 - Packet: ETH / IP / UDP / GENEVE
"""

import ipaddress

from scapy.all import (
    Packet, BitField, XShortField, ThreeBytesField, XByteField, Raw
)
from scapy.contrib.geneve import GENEVE
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from scapy.layers.inet6 import IPv6

from trex.stl.api import *
from TrafficStreamsJsonClass import TrafficStreamsJsonClass


class Geneve(Packet):
    """Defines custom Geneve Class."""
    name = "Geneve"
    fields_desc = [
        BitField("version", 0, 2),
        BitField("optionlen", 0, 6),
        BitField("oam", 0, 1),
        BitField("critical", 0, 1),
        BitField("reserved", 0, 6),
        XShortField("proto", 0x6558),
        ThreeBytesField("vni", 0),
        XByteField("reserved2", 0x00)
    ]


class TrafficStreams(TrafficStreamsJsonClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        super(TrafficStreamsJsonClass, self).__init__()

    def new_packet_header(self, key):
        """Define the packet modifications.

        :returns: List of VMs to be sent from the traffic generator.
        :rtype: list
        """
        header_data = self.stream_data[key]
        vm = []
        for vm_entry in header_data:
            value_list, size, offset = (
                vm_entry["value-list"],
                vm_entry["size"],
                vm_entry["offset"]
            )
            # reserved mac address size is 8 bytes so fill the rest with zeros
            if "mac" in vm_entry["name"]:
                for i, value in enumerate(vm_entry["value-list"]):
                    value += ":00:00"
                    value_list[i] = int(value.lower().replace(':', ''), 16)
            # replace only the second part of the IPv6 address
            if "ip" in vm_entry["name"] and vm_entry["size"] == 16:
                for i, value in enumerate(vm_entry["value-list"]):
                    value_list[i] = int.from_bytes(
                        ipaddress.IPv6Address(value).packed[8:],
                        byteorder="big"
                    )
                size, offset = 8, offset + 8
            vm.append(STLVmFlowVar(
                name=vm_entry["name"],
                value_list=value_list,
                size=size,
                op=vm_entry["op"]),
            )
            vm.append(STLVmWrFlowVar(
                fv_name=vm_entry["name"],
                pkt_offset=offset),
            )
        return vm

    def define_packets(self):
        """Defines the packets to be sent from the traffic generator.

        :returns: Base packets to be sent and transformation function.
        :rtype: tuple
        """
        base_pkt_data = self.stream_data["base-packet"]
        base_pkt = (
            Ether(
                src=base_pkt_data["outer-eth"]["src"],
                dst=base_pkt_data["outer-eth"]["dst"],
            ) /
            IP(
                src=base_pkt_data["outer-ip"]["src"],
                dst=base_pkt_data["outer-ip"]["dst"],
            ) /
            UDP(
                sport=int(base_pkt_data["outer-udp"]["src"]),
                dport=int(base_pkt_data["outer-udp"]["dst"]),
            ) /
            GENEVE(
                #         proto = 0x86dd,
                vni=base_pkt_data["encap-vni"],
            )
        )
        if "inner-eth" in base_pkt_data:
            base_pkt = base_pkt / (
                Ether(
                    src=base_pkt_data["inner-eth"]["src"],
                    dst=base_pkt_data["inner-eth"]["dst"],
                )
            )

        if ipaddress.ip_address(base_pkt_data["inner-ip"]["src"]).version == 6:
            base_pkt = base_pkt / (
                IPv6(
                    src=base_pkt_data["inner-ip"]["src"],
                    dst=base_pkt_data["inner-ip"]["dst"],
                )
            )
        else:
            base_pkt = base_pkt / (
                IP(
                    src=base_pkt_data["inner-ip"]["src"],
                    dst=base_pkt_data["inner-ip"]["dst"],
                )
            )
        base_pkt = base_pkt / (
            UDP(
                sport=int(base_pkt_data["inner-udp"]["src"]),
                dport=int(base_pkt_data["inner-udp"]["dst"]),
            )
        )
        length = self.stream_data["base-packet"]["length"]
        pkt = base_pkt / Raw(load="X" * (length - len(base_pkt)))

        outer_header_data = self.new_packet_header("outer-header")
        if "inner-l2-header" in self.stream_data:
            inner_header_data = self.new_packet_header("inner-l2-header")
        else:
            inner_header_data = self.new_packet_header("inner-l3-header")
        vm = STLScVmRaw(outer_header_data + inner_header_data)
        return pkt, vm


def register():
    """Register this traffic profile to T-Rex.

    Do not change this function.

    :return: Traffic streams.
    :rtype: Object
    """
    return TrafficStreams()
