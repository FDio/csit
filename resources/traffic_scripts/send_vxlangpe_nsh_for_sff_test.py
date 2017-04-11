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

"""Traffic script that sends an VxLAN-GPE+NSH packet
from TG to DUT.
"""
import sys
import time

from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.inet6 import IPv6
from scapy.all import Ether, Packet, Raw
from scapy.all import sendp

from resources.libraries.python.SFC.VerifyPacket import *
from resources.libraries.python.SFC.SFCConstants import SFCConstants as sfccon
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg

from robot.api import logger

def main():
    """Send VxLAN-GPE+NSH packet from TG to DUT.

    :raises: If the IP address is invalid.
    """
    args = TrafficScriptArg(
        ['src_mac', 'dst_mac', 'src_ip', 'dst_ip',
        'timeout', 'framesize', 'testtype'])

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    timeout = int(args.get_arg('timeout'))
    frame_size = int(args.get_arg('framesize'))
    test_type = args.get_arg('testtype')

    protocol = TCP
    source_port = sfccon.DEF_SRC_PORT
    destination_port = sfccon.DEF_DST_PORT

    ip_version = None
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        ip_version = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        ip_version = IPv6
    else:
        raise ValueError("Invalid IP version!")

    innerpkt = (Ether(src=src_mac, dst=dst_mac) /
               ip_version(src=src_ip, dst=dst_ip) /
               protocol(sport=int(source_port), dport=int(destination_port)))

    vxlangpe_nsh = '\x0c\x00\x00\x04\x00\x00\x0a\x00\x00\x06' \
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

    sendp(pkt_raw, iface=tx_if, count=3)

    time.sleep(timeout)

    # let us begin to check the sfc sff packet
    VerifyPacket.check_the_nsh_sfc_packet(frame_size, test_type)

    # we check all the fields about the sfc sff, this test will pass
    sys.exit(0)


if __name__ == "__main__":
    main()
