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

"""Traffic script - IPFIX listener."""

import sys
from ipaddress import IPv4Address, IPv6Address, AddressValueError

from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether
from scapy.packet import Padding

from resources.libraries.python.IPFIXUtil import IPFIXHandler, IPFIXData
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def valid_ipv4(ip):
    """Check if IP address has the correct IPv4 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv4 address format,
    otherwise return false.
    :rtype: bool
    """
    try:
        IPv4Address(unicode(ip))
        return True
    except (AttributeError, AddressValueError):
        return False


def valid_ipv6(ip):
    """Check if IP address has the correct IPv6 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv6 address format,
    otherwise return false.
    :rtype: bool
    """
    try:
        IPv6Address(unicode(ip))
        return True
    except (AttributeError, AddressValueError):
        return False


def main():
    """Send packets to VPP, then listen for IPFIX flow report. Verify that
    the correct packet count was reported."""
    args = TrafficScriptArg(
        ['src_mac', 'dst_mac', 'src_ip', 'dst_ip', 'protocol', 'port', 'count']
    )

    dst_mac = args.get_arg('dst_mac')
    src_mac = args.get_arg('src_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')

    protocol = args.get_arg('protocol')
    source_port = args.get_arg('port')
    destination_port = args.get_arg('port')
    count = int(args.get_arg('count'))

    txq = TxQueue(tx_if)
    rxq = RxQueue(tx_if)

    # generate simple packet based on arguments
    ip_version = None
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        ip_version = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        ip_version = IPv6
    else:
        ValueError("Invalid IP version!")

    if protocol.upper() == 'TCP':
        protocol = TCP
    elif protocol.upper() == 'UDP':
        protocol = UDP
    else:
        raise ValueError("Invalid type of protocol!")

    pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
               ip_version(src=src_ip, dst=dst_ip) /
               protocol(sport=int(source_port),
                        dport=int(destination_port)))

    if len(pkt_raw) == 60:
        pkt_ignore = pkt_raw
    else:
        padding = Padding()
        padding.load = '\x00'*(60-len(pkt_raw))
        pkt_ignore = pkt_raw/padding

    # send the generated packet
    for _ in range(count):
        txq.send(pkt_raw)

    # IPFIX listener loop
    ipfix = IPFIXHandler()
    while True:
        pkt = rxq.recv(5, ignore=[pkt_ignore for _ in range(count)])
        if pkt is None:
            continue
        elif not pkt.haslayer("IPFIXHeader"):
            continue
        else:
            if pkt.haslayer("IPFIXTemplate"):
                ipfix.update_template(pkt)
            if pkt.haslayer("IPFIXData"):
                total = pkt.getlayer(IPFIXData).packetTotalCount
                if total == count:
                    sys.exit(0)
                else:
                    raise Exception("IPFIX reported wrong packet count. Count "
                                    "was {0} but should be {1}".format(total,
                                                                       count))


if __name__ == "__main__":

    main()
