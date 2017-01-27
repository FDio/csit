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

    sent = []

    if ptype == "ARP":
        pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                   ARP(hwsrc=src_mac, hwdst="00:00:00:00:00:00",
                       psrc=src_ip, pdst=dst_ip, op="who-has"))
    elif ptype == "ICMP":
        if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       IP(src=src_ip, dst=dst_ip) /
                       ICMP(type="echo-request"))
        else:
            raise ValueError("IP addresses not in correct format")
    elif ptype == "ICMPv6":
        if valid_ipv6(src_ip) and valid_ipv6(dst_ip):
            pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
                       IPv6(src=src_ip, dst=dst_ip) /
                       ICMPv6EchoRequest())
        else:
            raise ValueError("IPv6 addresses not in correct format")
    else:
        raise RuntimeError("Unexpected payload type.")

    txq.send(pkt_raw)
    sent.append(auto_pad(pkt_raw))
    ether = rxq_mirrored.recv(2)

    # Receive copy of Rx packet.
    if ether is None:
        raise RuntimeError("Rx timeout of mirrored Rx packet")
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
    print("Mirrored Rx packet check OK.\n")

    # Receive reply on TG Tx port.
    ether_repl = rxq_tx.recv(2, sent)
    if ether_repl is None:
        raise RuntimeError("Reply not received on TG Tx port.")
    else:
        print("Reply received on TG Tx port.\n")

    # Receive copy of Tx packet.
    ether = rxq_mirrored.recv(2)
    if ether is None:
        raise RuntimeError("Rx timeout of mirrored Tx packet")
    if str(ether) != str(ether_repl):
        print("Mirrored Tx packet doesn't match the received Tx packet.")
        if ether.src != ether_repl.src or ether.dst != ether_repl.dst:
            raise RuntimeError("MAC mismatch in mirrored Tx packet.")
        if ptype == "ARP":
            if not ether.haslayer(ARP):
                raise RuntimeError("Mirrored Tx packet is not an ARP packet.")
            if ether['ARP'].op != ether_repl['ARP'].op:  # 2=is_at
                raise RuntimeError("ARP operational code mismatch "
                                   "in mirrored Tx packet.")
            if ether['ARP'].hwsrc != ether_repl['ARP'].hwsrc\
                    or ether['ARP'].hwdst != ether_repl['ARP'].hwdst:
                raise RuntimeError("MAC mismatch in mirrored Tx ARP packet.")
            if ether['ARP'].psrc != ether_repl['ARP'].psrc\
                    or ether['ARP'].pdst != ether_repl['ARP'].pdst:
                raise RuntimeError("IP address mismatch in mirrored "
                                   "Tx ARP packet.")
        elif ptype == "ICMP":
            if not ether.haslayer(IP):
                raise RuntimeError("Mirrored Tx packet is not an IPv4 packet.")
            if ether['IP'].src != ether_repl['IP'].src\
                    or ether['IP'].dst != ether_repl['IP'].dst:
                raise RuntimeError("IP address mismatch in mirrored "
                                   "Tx IPv4 packet.")
            if not ether.haslayer(ICMP):
                raise RuntimeError("Mirrored Tx packet is not an ICMP packet.")
            if ether['ICMP'].type != ether_repl['ICMP'].type:  # 0=echo-reply
                raise RuntimeError("ICMP packet type mismatch "
                                   "in mirrored Tx packet.")
        elif ptype == "ICMPv6":
            if not ether.haslayer(IPv6):
                raise RuntimeError("Mirrored Tx packet is not an IPv6 packet.")
            if ether['IPv6'].src != ether_repl['IPv6'].src\
                    or ether['IPv6'].dst != ether_repl['IPv6'].dst:
                raise RuntimeError("IP address mismatch in mirrored "
                                   "Tx IPv6 packet.")
            if ether[2].name != ether_repl[2].name:
                raise RuntimeError("ICMPv6 message type mismatch "
                                   "in mirrored Tx packet.")
    print("Mirrored Tx packet check OK.\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
