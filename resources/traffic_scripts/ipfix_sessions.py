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

from resources.libraries.python.telemetry.IPFIXUtil import IPFIXHandler, \
    IPFIXData
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue, auto_pad
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


def verify_data(data, count, src_ip, dst_ip, protocol):
    """Compare data in IPFIX flow report against parameters used to send test
     packets.

     :param data: Dictionary of fields in IPFIX flow report.
     :param count: Number of packets expected.
     :param src_ip: Expected source IP address.
     :param dst_ip: Expected destination IP address.
     :param protocol: Expected protocol, TCP or UDP.
     :type data: dict
     :type count: int
     :type src_ip: str
     :type dst_ip: str
     :type protocol: scapy.layers
     """

    # verify packet count
    if data["packetTotalCount"] != count:
        raise RuntimeError(
            "IPFIX reported wrong packet count. Count was {0},"
            " but should be {1}".format(data["packetTotalCount"], count))
    # verify IP addresses
    keys = data.keys()
    e = "{0} mismatch. Packets used {1}, but were classified as {2}."
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        if "IPv4_src" in keys:
            if data["IPv4_src"] != src_ip:
                raise RuntimeError(
                    e.format("Source IP", src_ip, data["IPv4_src"]))
        if "IPv4_dst" in keys:
            if data["IPv4_dst"] != dst_ip:
                raise RuntimeError(
                    e.format("Destination IP", dst_ip, data["IPv4_dst"]))
    else:
        if "IPv6_src" in keys:
            if data["IPv6_src"] != src_ip:
                raise RuntimeError(
                    e.format("Source IP", src_ip, data["IPv6_src"]))
        if "IPv6_dst" in keys:
            if data["IPv6_dst"] != dst_ip:
                raise RuntimeError(
                    e.format("Source IP", src_ip, data["IPv6_dst"]))
    # verify protocol ID
    if "Protocol_ID" in keys:
        if protocol == TCP and int(data["Protocol_ID"]) != 6:
            raise RuntimeError(
                "TCP Packets were classified as not TCP.")
        if protocol == UDP and int(data["Protocol_ID"]) != 17:
            raise RuntimeError(
                "UDP Packets were classified as not UDP.")
    # return port number
    for item in ("src_port", "tcp_src_port", "udp_src_port",
                 "dst_port", "tcp_dst_port", "udp_dst_port"):
        if item in keys:
            return int(data[item])
        else:
            raise RuntimeError("Data contains no port information.")


def main():
    """Send packets to VPP, then listen for IPFIX flow report. Verify that
    the correct packet count was reported."""
    args = TrafficScriptArg(
        ['src_mac', 'dst_mac', 'src_ip', 'dst_ip', 'protocol', 'port', 'count',
         'sessions']
    )

    dst_mac = args.get_arg('dst_mac')
    src_mac = args.get_arg('src_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')

    protocol = args.get_arg('protocol')
    count = int(args.get_arg('count'))
    sessions = int(args.get_arg('sessions'))

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

    packets = []
    for x in range(sessions):
        pkt = (Ether(src=src_mac, dst=dst_mac) /
               ip_version(src=src_ip, dst=dst_ip) /
               protocol(sport=x, dport=x))
        pkt = auto_pad(pkt)
        packets.append(pkt)

    # do not print details for sent packets
    verbose = False
    print("Sending more than one packet. Details will be filtered for "
          "all packets sent.")

    ignore = []
    for x in range(sessions):
        for _ in range(count):
            txq.send(packets[x], verbose=verbose)
            ignore.append(packets[x])

    # allow scapy to recognize IPFIX headers and templates
    ipfix = IPFIXHandler()

    # clear receive buffer
    while True:
        pkt = rxq.recv(1, ignore=packets, verbose=verbose)
        if pkt is None:
            break

    data = None
    ports = [x for x in range(sessions)]

    # get IPFIX template and data
    while True:
        pkt = rxq.recv(5)
        if pkt is None:
            raise RuntimeError("RX timeout")
        if pkt.haslayer("IPFIXHeader"):
            if pkt.haslayer("IPFIXTemplate"):
                # create or update template for IPFIX data packets
                ipfix.update_template(pkt)
            elif pkt.haslayer("IPFIXData"):
                for x in range(sessions):
                    try:
                        data = pkt.getlayer(IPFIXData, x+1).fields
                    except AttributeError:
                        raise RuntimeError("Could not find data layer "
                                           "#{0}".format(x+1))
                    port = verify_data(data, count, src_ip, dst_ip, protocol)
                    if port in ports:
                        ports.remove(port)
                    else:
                        raise RuntimeError("Unexpected or duplicate port {0} "
                                           "in flow report.".format(port))
                print("All {0} sessions verified "
                      "with packet count {1}.".format(sessions, count))
                sys.exit(0)
            else:
                raise RuntimeError("Unable to parse IPFIX template "
                                   "or data set.")
        else:
            raise RuntimeError("Received non-IPFIX packet or IPFIX header was"
                               "not recognized.")

if __name__ == "__main__":

    main()
