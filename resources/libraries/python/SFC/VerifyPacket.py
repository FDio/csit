#!/usr/bin/env python
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
This module defines the common functions.
"""

import ipaddress

from scapy.layers.inet import IP, UDP
from scapy.all import Raw
from resources.libraries.python.SFC.SFCConstants import SFCConstants as sfccon
from resources.libraries.python.SFC.TunnelProtocol import VxLAN, VxLANGPE, NSH


def valid_ipv4(ipaddr):
    """Check if IP address has the correct IPv4 address format.

    :param ipaddr: IP address.
    :type ipaddr: str
    :returns: True in case of correct IPv4 address format,
              otherwise return False.
    :rtype: bool
    """
    try:
        ipaddress.IPv4Address(unicode(ipaddr))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def valid_ipv6(ipaddr):
    """Check if IP address has the correct IPv6 address format.

    :param ipaddr: IP address.
    :type ipaddr: str
    :returns: True in case of correct IPv6 address format,
              otherwise return False.
    :rtype: bool
    """
    try:
        ipaddress.IPv6Address(unicode(ipaddr))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


class VerifyPacket(object):
    """Define some functions for the test filed verify."""

    @staticmethod
    def check_vxlan_protocol(payload_data):
        """
        verify the vxlan protocol in the payload data.

        :param payload_data: the payload data in the packet.
        :type payload_data: str
        :raises RuntimeError: If the vxlan protocol field verify fails.
        """
        # get the vxlan packet and check it
        vxlan_pkt = VxLAN(payload_data[0:8])
        if vxlan_pkt.flags != sfccon.VxLAN_FLAGS:
            raise RuntimeError("Unexpected Vxlan flags: {0}".
                               format(vxlan_pkt.flags))

        if vxlan_pkt.vni != sfccon.VxLAN_DEFAULT_VNI:
            raise RuntimeError("Unexpected VNI flag: {0}".format(vxlan_pkt.vni))

    @staticmethod
    def check_vxlangpe_nsh_protocol(payload_data, test_type):
        """
        verify the vxlangpe and nsh protocol in the payload data.

        :param payload_data: the payload data in the packet.
        :param test_type: the functional test type.
        :type payload_data: str
        :type test_type: str
        :raises RuntimeError: If the vxlangpe and nsh protocol
                              field verify fails.
        """
        # get the vxlan-gpe packet and check it
        vxlangpe_pkt = VxLANGPE(payload_data[0:8])
        if vxlangpe_pkt.flags != sfccon.VxLANGPE_FLAGS:
            raise RuntimeError("Unexpected Vxlan-GPE flags: {0}".
                               format(vxlangpe_pkt.flags))

        if vxlangpe_pkt.nextproto != sfccon.VxLANGPE_NEXT_PROTOCOL:
            raise RuntimeError("next protocol not the NSH")

        if vxlangpe_pkt.vni != sfccon.VxLANGPE_DEFAULT_VNI:
            raise RuntimeError("Unexpected VNI flag: {0}".
                               format(vxlangpe_pkt.vni))

        # get the NSH packet and check it
        nsh_pkt = NSH(payload_data[8:32])
        if nsh_pkt.Version != 0:
            raise RuntimeError("Unexpected NSH version: {0}".
                               format(nsh_pkt.Version))

        if nsh_pkt.OAM != 0 and nsh_pkt.OAM != 1:
            raise RuntimeError("Unexpected NSH OAM: {0}".
                               format(nsh_pkt.OAM))

        if nsh_pkt.length != sfccon.NSH_HEADER_LENGTH:
            raise RuntimeError("NSH length {0} incorrect".
                               format(nsh_pkt.length))

        if nsh_pkt.MDtype != sfccon.NSH_DEFAULT_MDTYPE:
            raise RuntimeError("NSH MD-Type {0} incorrect".
                               format(nsh_pkt.MDtype))

        if nsh_pkt.nextproto != sfccon.NSH_NEXT_PROTOCOL:
            raise RuntimeError("NSH next protocol {0} incorrect".
                               format(nsh_pkt.nextproto))

        if test_type == "Proxy Outbound" or test_type == "SFF":
            expect_nsi = sfccon.NSH_DEFAULT_NSI - 1
        else:
            expect_nsi = sfccon.NSH_DEFAULT_NSI

        nsp_nsi = nsh_pkt.nsp_nsi
        nsp = nsp_nsi >> 8
        nsi = nsp_nsi & 0x000000FF
        if nsp != sfccon.NSH_DEFAULT_NSP:
            raise RuntimeError("NSH Service Path ID {0} incorrect".format(nsp))

        if nsi != expect_nsi:
            raise RuntimeError("NSH Service Index {0} incorrect".format(nsi))

        nsh_c1 = nsh_pkt.c1
        if nsh_c1 != sfccon.NSH_DEFAULT_C1:
            raise RuntimeError("NSH c1 {0} incorrect".format(nsh_c1))

        nsh_c2 = nsh_pkt.c2
        if nsh_c2 != sfccon.NSH_DEFAULT_C2:
            raise RuntimeError("NSH c2 {0} incorrect".format(nsh_c2))

        nsh_c3 = nsh_pkt.c3
        if nsh_c3 != sfccon.NSH_DEFAULT_C3:
            raise RuntimeError("NSH c3 {0} incorrect".format(nsh_c3))

        nsh_c4 = nsh_pkt.c4
        if nsh_c4 != sfccon.NSH_DEFAULT_C4:
            raise RuntimeError("NSH c4 {0} incorrect".format(nsh_c4))


    @staticmethod
    def check_the_nsh_sfc_packet(ether, frame_size, test_type):
        """
        verify the NSH SFC functional test loopback packet field
        is correct.

        :param ether: The Ethernet packet data.
        :param frame_size: The origin frame size.
        :param test_type: The test type.
                         (Classifier, Proxy Inbound, Proxy Outbound, SFF).

        :type ether: scapy.Ether
        :type frame_size: Integer
        :type test_type: str
        :raises RuntimeError: If the packet field verify fails.
        """

        origin_size = int(frame_size)
        if test_type == "Classifier":
            expect_pkt_len = origin_size + 74 - 4
        elif test_type == "Proxy Inbound":
            expect_pkt_len = origin_size - 24 - 4
        elif test_type == "Proxy Outbound":
            expect_pkt_len = origin_size + 24 - 4
        else:
            expect_pkt_len = origin_size - 4

        recv_pkt_len = len(ether)
        if recv_pkt_len != expect_pkt_len:
            raise RuntimeError("Received packet size {0} not "
                               "the expect size {1}".format(recv_pkt_len,
                                                            expect_pkt_len))

        if not ether.haslayer(IP):
            raise RuntimeError("Not a IPv4 packet")

        pkt_proto = ether[IP].proto
        if pkt_proto != sfccon.UDP_PROTOCOL:
            raise RuntimeError("Not a UDP packet , {0}".format(pkt_proto))

        if test_type == "Proxy Inbound":
            expect_udp_port = sfccon.VxLAN_UDP_PORT
        else:
            expect_udp_port = sfccon.VxLANGPE_UDP_PORT

        dst_port = ether[UDP].dport
        if dst_port != expect_udp_port:
            raise RuntimeError("UDP dest port must be {0}, {1}".
                               format(expect_udp_port, dst_port))

        payload_data = ether[Raw].load

        if test_type == "Proxy Inbound":
            VerifyPacket.check_vxlan_protocol(payload_data)
        else:
            VerifyPacket.check_vxlangpe_nsh_protocol(payload_data, test_type)
