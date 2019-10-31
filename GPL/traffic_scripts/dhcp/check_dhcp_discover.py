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

"""Traffic script that receives an DHCP packet on given interface and check if
is correct DHCP DISCOVER message.
"""

import sys

from scapy.layers.inet import UDP_SERVICES

from ..PacketVerifier import RxQueue
from ..TrafficScriptArg import TrafficScriptArg


def main():
    args = TrafficScriptArg(['rx_src_mac'], ['hostname'])

    rx_if = args.get_arg('rx_if')
    rx_src_mac = args.get_arg('rx_src_mac')
    hostname = args.get_arg('hostname')

    rx_dst_mac = 'ff:ff:ff:ff:ff:ff'
    rx_src_ip = '0.0.0.0'
    rx_dst_ip = '255.255.255.255'
    boot_request = 1
    dhcp_magic = 'c\x82Sc'

    rxq = RxQueue(rx_if)

    ether = rxq.recv(10)

    if ether is None:
        raise RuntimeError("DHCP DISCOVER Rx timeout.")

    if ether.dst != rx_dst_mac:
        raise RuntimeError("Destination MAC address error.")
    print "Destination MAC address: OK."

    if ether.src != rx_src_mac:
        raise RuntimeError("Source MAC address error.")
    print "Source MAC address: OK."

    if ether['IP'].dst != rx_dst_ip:
        raise RuntimeError("Destination IP address error.")
    print "Destination IP address: OK."

    if ether['IP'].src != rx_src_ip:
        raise RuntimeError("Source IP address error.")
    print "Source IP address: OK."

    if ether['IP']['UDP'].dport != UDP_SERVICES.bootps:
        raise RuntimeError("UDP destination port error.")
    print "UDP destination port: OK."

    if ether['IP']['UDP'].sport != UDP_SERVICES.bootpc:
        raise RuntimeError("UDP source port error.")
    print "UDP source port: OK."

    bootp = ether['BOOTP']

    if bootp.op != boot_request:
        raise RuntimeError("BOOTP message type error.")
    print "BOOTP message type: OK"

    if bootp.ciaddr != '0.0.0.0':
        raise RuntimeError("BOOTP client IP address error.")
    print "BOOTP client IP address: OK"

    if bootp.yiaddr != '0.0.0.0':
        raise RuntimeError("BOOTP 'your' (client) IP address error.")
    print "BOOTP 'your' (client) IP address: OK"

    if bootp.siaddr != '0.0.0.0':
        raise RuntimeError("BOOTP next server IP address error.")
    print "BOOTP next server IP address: OK"

    if bootp.giaddr != '0.0.0.0':
        raise RuntimeError("BOOTP relay agent IP address error.")
    print "BOOTP relay agent IP address: OK"

    chaddr = bootp.chaddr[:bootp.hlen].encode('hex')
    if chaddr != rx_src_mac.replace(':', ''):
        raise RuntimeError("BOOTP client hardware address error.")
    print "BOOTP client hardware address: OK"

    # Check hostname
    if bootp.sname != 64*'\x00':
        raise RuntimeError("BOOTP server name error.")
    print "BOOTP server name: OK"

    # Check boot file
    if bootp.file != 128*'\x00':
        raise RuntimeError("BOOTP boot file name error.")
    print "BOOTP boot file name: OK"

    # Check bootp magic
    if bootp.options != dhcp_magic:
        raise RuntimeError("DHCP magic error.")
    print "DHCP magic: OK"

    # Check options
    dhcp_options = ether['DHCP options'].options

    # Option 12
    hn = filter(lambda x: x[0] == 'hostname', dhcp_options)
    if hostname:
        try:
            if hn[0][1] != hostname:
                raise RuntimeError("Client's hostname doesn't match.")
        except IndexError:
            raise RuntimeError("Option list doesn't contain hostname option.")
    else:
        if len(hn) != 0:
            raise RuntimeError("Option list contains hostname option.")
    print "Option 12 hostname: OK"

    # Option 53
    mt = filter(lambda x: x[0] == 'message-type', dhcp_options)[0][1]
    if mt != 1:
        raise RuntimeError("Option 53 message-type error.")
    print "Option 53 message-type: OK"

    # Option 55
    prl = filter(lambda x: x[0] == 'param_req_list', dhcp_options)[0][1]
    if prl != '\x01\x1c\x02\x03\x0f\x06w\x0c,/\x1ay*':
        raise RuntimeError("Option 55 param_req_list error.")
    print "Option 55 param_req_list: OK"

    # Option 255
    if 'end' not in dhcp_options:
        raise RuntimeError("end option error.")
    print "end option: OK"

    sys.exit(0)


if __name__ == "__main__":
    main()
