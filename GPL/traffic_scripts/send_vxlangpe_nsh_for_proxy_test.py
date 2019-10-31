#!/usr/bin/env python

# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.

"""Traffic script that sends an VxLAN-GPE+NSH packet
from TG to DUT.
"""
import sys

from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.all import Ether, Packet, Raw

from .SFC.VerifyPacket import *
from .SFC.SFCConstants import SFCConstants as SfcCon
from .TrafficScriptArg import TrafficScriptArg
from .PacketVerifier import RxQueue, TxQueue


def main():
    """Send VxLAN-GPE+NSH packet from TG to DUT.

    :raises: If the IP address is invalid.
    """
    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip',
                             'timeout', 'framesize', 'testtype'])

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    timeout = max(2, int(args.get_arg('timeout')))
    frame_size = int(args.get_arg('framesize'))
    test_type = args.get_arg('testtype')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    protocol = TCP
    source_port = SfcCon.DEF_SRC_PORT
    destination_port = SfcCon.DEF_DST_PORT

    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        ip_version = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        ip_version = IPv6
    else:
        raise ValueError("Invalid IP version!")

    innerpkt = (Ether(src=src_mac, dst=dst_mac) /
                ip_version(src=src_ip, dst=dst_ip) /
                protocol(sport=int(source_port), dport=int(destination_port)))

    vxlangpe_nsh = '\x0c\x00\x00\x04\x00\x00\x09\x00\x00\x06' \
                   '\x01\x03\x00\x00\xb9\xff\xC0\xA8\x32\x4B' \
                   '\x00\x00\x00\x09\xC0\xA8\x32\x48\x03\x00\x12\xB5'

    raw_data = vxlangpe_nsh + str(innerpkt)

    pkt_header = (Ether(src=src_mac, dst=dst_mac) /
                  ip_version(src=src_ip, dst=dst_ip) /
                  UDP(sport=int(source_port), dport=4790) /
                  Raw(load=raw_data))

    fsize_no_fcs = frame_size - 4
    pad_len = max(0, fsize_no_fcs - len(pkt_header))
    pad_data = "A" * pad_len

    pkt_raw = pkt_header / Raw(load=pad_data)

    # Send created packet on one interface and receive on the other
    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    while True:
        ether = rxq.recv(timeout)
        if ether is None:
            raise RuntimeError('No packet is received!')

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    # let us begin to check the proxy inbound packet
    VerifyPacket.check_the_nsh_sfc_packet(ether, frame_size, test_type)

    # we check all the fields about the proxy inbound, this test will pass
    sys.exit(0)


if __name__ == "__main__":
    main()
