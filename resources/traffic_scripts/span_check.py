#!/usr/bin/env python
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

"""Traffic script that sends an IP ICMPv4/ICMPv6 packet from one interface
to the other. Source and destination IP addresses and source and destination
MAC addresses are checked in received packet.
"""

import sys
import ipaddress

from scapy.layers.inet import IP, ICMP, ARP
from scapy.layers.inet6 import IPv6, ICMPv6EchoRequest, ICMPv6EchoReply
from scapy.layers.l2 import Ether

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue, auto_pad
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def valid_ipv4(address):
    """Check if IP address has the correct IPv4 address format.

    :param address: IP address.
    :type address: str
    :return: True in case of correct IPv4 address format,
    otherwise return false.
    :rtype: bool
    """
    try:
        ipaddress.IPv4Address(unicode(address))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def valid_ipv6(address):
    """Check if IP address has the correct IPv6 address format.

    :param address: IP address.
    :type address: str
    :return: True in case of correct IPv6 address format,
    otherwise return false.
    :rtype: bool
    """
    try:
        ipaddress.IPv6Address(unicode(address))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def main():
    """Send a simple L2 or ICMP packet from one TG interface to DUT, then
    receive a copy of the packet on the second TG interface, and a copy of
    the ICMP reply."""
    args = TrafficScriptArg(
        ['tg_src_mac', 'src_ip', 'dst_ip', 'dut_if1_mac', 'ptype'])

    src_mac = args.get_arg('tg_src_mac')
    dst_mac = args.get_arg('dut_if1_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    ptype = args.get_arg('ptype')

    rxq_mirrored = RxQueue(rx_if)
    rxq_tx = RxQueue(tx_if)
    txq = TxQueue(tx_if)

    if ptype == "ARP":
        pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                   ARP(hwsrc=src_mac, hwdst="00:00:00:00:00:00",
                       psrc=src_ip, pdst=dst_ip, op="who-has"))
    elif ptype == "ICMP":
        if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       IP(src=src_ip, dst=dst_ip) /
                       ICMP(type="echo-request"))
        elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       IPv6(src=src_ip, dst=dst_ip) /
                       ICMPv6EchoRequest())
        else:
            raise ValueError("IP not in correct format")
    else:
        raise RuntimeError("Unexpected payload type.")

    txq.send(pkt_raw)
    ether = rxq_mirrored.recv(2)

    # Receive copy of Rx packet.
    if ether is None:
        raise RuntimeError("Rx timeout")
    pkt = auto_pad(pkt_raw)
    if str(ether) != str(pkt):
        print("Mirrored Rx packet doesn't match the original Rx packet.")
        if ether.src != src_mac or ether.dst != dst_mac:
            raise RuntimeError("MAC mismatch in mirrored Rx packet.")
        if ptype == "ARP":
            if not ether.haslayer(ARP):
                raise RuntimeError("Mirrored Rx packet is not an ARP packet.")
            if ether['ARP'].op != 1:  # 1=who-has
                raise RuntimeError("Mirrored Rx packet is not an ARP request.")
            if ether['ARP'].hwsrc != src_mac or ether['ARP'].hwdst != dst_mac:
                raise RuntimeError("MAC mismatch in mirrored Rx ARP packet.")
            if ether['ARP'].psrc != src_ip or ether['ARP'].pdst != dst_ip:
                raise RuntimeError("IP address mismatch in mirrored "
                                   "Rx ARP packet.")
        elif ptype == "ICMP":
            if not ether.haslayer(IP):
                raise RuntimeError("Mirrored Rx packet is not an IPv4 packet.")
            if ether['IP'].src != src_ip or ether['IP'].dst != dst_ip:
                raise RuntimeError("IP address mismatch in mirrored "
                                   "Rx IPv4 packet.")
            if not ether.haslayer(ICMP):
                raise RuntimeError("Mirrored Rx packet is not an ICMP packet.")
            if ether['ICMP'].type != 8:  # 8=echo-request
                raise RuntimeError("Mirrored Rx packet is not an ICMP "
                                   "echo request.")
        elif ptype == "ICMPv6":
            if not ether.haslayer(IPv6):
                raise RuntimeError("Mirrored Rx packet is not an IPv6 packet.")
            if ether['IPv6'].src != src_ip or ether['IPv6'].dst != dst_ip:
                raise RuntimeError("IP address mismatch in mirrored "
                                   "Rx IPv6 packet.")
            if not ether.haslayer(ICMPv6EchoRequest):
                raise RuntimeError("Mirrored Rx packet is not an ICMPv6 "
                                   "echo request.")
    print("Mirrored Rx packet check OK.")

    # Receive reply on TG Tx port.
    ether_2 = rxq_tx.recv(2)
    if ether_2 is None:
        tx_status = "Reply not received on TG Tx port."
    else:
        tx_status = "Reply received on TG Tx port."
    print(tx_status)
    
    # Receive copy of Tx packet.
    ether = rxq.recv(2)
    if ether is None:
        raise RuntimeError("Rx timeout")
    if ether.src != dst_mac or ether.dst != src_mac:
        raise RuntimeError("MAC mismatch in mirrored Tx packet.")
    if ptype == "ARP":
        if not ether.haslayer(ARP):
            raise RuntimeError("Mirrored Tx packet is not an ARP packet.")
        if ether['ARP'].op != 2:  # 2=is_at
            raise RuntimeError("Mirrored Tx packet is not an ARP reply.")
        if ether['ARP'].hwsrc != dst_mac or ether['ARP'].hwdst != src_mac:
            raise RuntimeError("MAC mismatch in mirrored Tx ARP packet.")
        if ether['ARP'].psrc != dst_ip or ether['ARP'].pdst != src_ip:
            raise RuntimeError("IP address mismatch in mirrored "
                               "Tx ARP packet.")
    elif ptype == "ICMP":
        if not ether.haslayer(IP):
            raise RuntimeError("Mirrored Tx packet is not an IPv4 packet.")
        if ether['IP'].src != dst_ip or ether['IP'].dst != src_ip:
            raise RuntimeError("IP address mismatch in mirrored "
                               "Tx IPv4 packet.")
        if not ether.haslayer(ICMP):
            raise RuntimeError("Mirrored Tx packet is not an ICMP packet.")
        if ether['ICMP'].type != 0:  # 0=echo-reply
            raise RuntimeError("Mirrored Tx packet is not an ICMP "
                               "echo reply.")
    elif ptype == "ICMPv6":
        if not ether.haslayer(IPv6):
            raise RuntimeError("Mirrored Tx packet is not an IPv6 packet.")
        if ether['IPv6'].src != dst_ip or ether['IPv6'].dst != src_ip:
            raise RuntimeError("IP address mismatch in mirrored "
                               "Tx IPv6 packet.")
        if not ether.haslayer(ICMPv6EchoReply):
            raise RuntimeError("Mirrored Tx packet is not an ICMPv6 "
                               "echo reply.")
    print("Mirrored Tx packet check OK.")

    sys.exit(0)


if __name__ == "__main__":
    main()
