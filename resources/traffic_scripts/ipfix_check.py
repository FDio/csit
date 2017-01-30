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
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue, auto_pad
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from resources.libraries.python.telemetry.IPFIXUtil import IPFIXHandler, \
    IPFIXData


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
    source_port = int(args.get_arg('port'))
    destination_port = int(args.get_arg('port'))
    count = int(args.get_arg('count'))

    txq = TxQueue(tx_if)
    rxq = RxQueue(tx_if)

    # generate simple packet based on arguments
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        ip_version = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        ip_version = IPv6
    else:
        raise ValueError("Invalid IP version!")

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

    # do not print details for sent packets when sending more than one
    if count > 1:
        verbose = False
        print("Sending more than one packet. Details will be filtered for "
              "all packets sent.")
    else:
        verbose = True

    pkt_pad = auto_pad(pkt_raw)
    ignore = []
    for _ in range(count):
        txq.send(pkt_pad, verbose=verbose)
        ignore.append(pkt_pad)

    # allow scapy to recognize IPFIX headers and templates
    ipfix = IPFIXHandler()
    data = None
    # get IPFIX template and data
    while True:
        pkt = rxq.recv(10, ignore=ignore, verbose=verbose)
        if pkt is None:
            raise RuntimeError("RX timeout")
        if pkt.haslayer("IPFIXHeader"):
            if pkt.haslayer("IPFIXTemplate"):
                # create or update template for IPFIX data packets
                ipfix.update_template(pkt)
            elif pkt.haslayer("IPFIXData"):
                data = pkt.getlayer(IPFIXData).fields
                break
            else:
                raise RuntimeError("Unable to parse IPFIX set after header.")
        else:
            raise RuntimeError("Received non-IPFIX packet or IPFIX header "
                               "not recognized.")

    # verify packet count
    if data["packetTotalCount"] != count:
        raise RuntimeError(
            "IPFIX reported wrong packet count. Count was {0},"
            " but should be {1}".format(data["packetTotalCount"], count))
    # verify IP addresses
    keys = data.keys()
    err = "{0} mismatch. Packets used {1}, but were classified as {2}."
    if ip_version == IP:
        if "IPv4_src" in keys:
            if data["IPv4_src"] != src_ip:
                raise RuntimeError(
                    err.format("Source IP", src_ip, data["IPv4_src"]))
        if "IPv4_dst" in keys:
            if data["IPv4_dst"] != dst_ip:
                raise RuntimeError(
                    err.format("Destination IP", dst_ip, data["IPv4_dst"]))
    else:
        if "IPv6_src" in keys:
            if data["IPv6_src"] != src_ip:
                raise RuntimeError(
                    err.format("Source IP", src_ip, data["IPv6_src"]))
        if "IPv6_dst" in keys:
            if data["IPv6_dst"] != dst_ip:
                raise RuntimeError(
                    err.format("Source IP", src_ip, data["IPv6_dst"]))
    # verify port numbers
    for item in ("src_port", "tcp_src_port", "udp_src_port"):
        try:
            if int(data[item]) != source_port:
                raise RuntimeError(
                    err.format("Source port", source_port, data[item]))
        except KeyError:
            pass
    for item in ("dst_port", "tcp_dst_port", "udp_dst_port"):
        try:
            if int(data[item]) != destination_port:
                raise RuntimeError(
                    err.format("Source port", destination_port, data[item]))
        except KeyError:
            pass
    # verify protocol ID
    if "Protocol_ID" in keys:
        if protocol == TCP and int(data["Protocol_ID"]) != 6:
            raise RuntimeError("TCP Packets were classified as not TCP.")
        if protocol == UDP and int(data["Protocol_ID"]) != 17:
            raise RuntimeError("UDP Packets were classified as not UDP.")
    sys.exit(0)


if __name__ == "__main__":
    main()
