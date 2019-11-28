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

"""Traffic script that receives an DHCP packet on given interface and check if
is correct DHCP DISCOVER message.
"""

import sys

from scapy.layers.inet import UDP_SERVICES

from resources.libraries.python.PacketVerifier import RxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    args = TrafficScriptArg([u'rx_src_mac'], [u'hostname'])

    rx_if = args.get_arg(u'rx_if')
    rx_src_mac = args.get_arg(u'rx_src_mac')
    hostname = args.get_arg(u'hostname')

    rx_dst_mac = u'ff:ff:ff:ff:ff:ff'
    rx_src_ip = u'0.0.0.0'
    rx_dst_ip = u'255.255.255.255'
    boot_request = 1
    dhcp_magic = u'c\x82Sc'

    rxq = RxQueue(rx_if)

    ether = rxq.recv(10)

    if ether is None:
        raise RuntimeError(u"DHCP DISCOVER Rx timeout.")

    if ether.dst != rx_dst_mac:
        raise RuntimeError(u"Destination MAC address error.")
    print (u"Destination MAC address: OK.")

    if ether.src != rx_src_mac:
        raise RuntimeError(u"Source MAC address error.")
    print (u"Source MAC address: OK.")

    if ether[u'IP'].dst != rx_dst_ip:
        raise RuntimeError(u"Destination IP address error.")
    print (u"Destination IP address: OK.")

    if ether[u'IP'].src != rx_src_ip:
        raise RuntimeError(u"Source IP address error.")
    print (u"Source IP address: OK.")

    if ether[u'IP'][u'UDP'].dport != UDP_SERVICES.bootps:
        raise RuntimeError(u"UDP destination port error.")
    print (u"UDP destination port: OK.")

    if ether[u'IP'][u'UDP'].sport != UDP_SERVICES.bootpc:
        raise RuntimeError(u"UDP source port error.")
    print (u"UDP source port: OK.")

    bootp = ether[u'BOOTP']

    if bootp.op != boot_request:
        raise RuntimeError(u"BOOTP message type error.")
    print (u"BOOTP message type: OK")

    if bootp.ciaddr != u'0.0.0.0':
        raise RuntimeError(u"BOOTP client IP address error.")
    print (u"BOOTP client IP address: OK")

    if bootp.yiaddr != u'0.0.0.0':
        raise RuntimeError(u"BOOTP u'your' (client) IP address error.")
    print (u"BOOTP u'your' (client) IP address: OK")

    if bootp.siaddr != u'0.0.0.0':
        raise RuntimeError(u"BOOTP next server IP address error.")
    print (u"BOOTP next server IP address: OK")

    if bootp.giaddr != u'0.0.0.0':
        raise RuntimeError(u"BOOTP relay agent IP address error.")
    print (u"BOOTP relay agent IP address: OK")

    chaddr = bootp.chaddr[:bootp.hlen].encode(u'hex')
    if chaddr != rx_src_mac.replace(u':', u''):
        raise RuntimeError(u"BOOTP client hardware address error.")
    print (u"BOOTP client hardware address: OK")

    # Check hostname
    if bootp.sname != 64*'\x00':
        raise RuntimeError(u"BOOTP server name error.")
    print (u"BOOTP server name: OK")

    # Check boot file
    if bootp.file != 128*'\x00':
        raise RuntimeError(u"BOOTP boot file name error.")
    print (u"BOOTP boot file name: OK")

    # Check bootp magic
    if bootp.options != dhcp_magic:
        raise RuntimeError(u"DHCP magic error.")
    print (u"DHCP magic: OK")

    # Check options
    dhcp_options = ether[u'DHCP options'].options

    # Option 12
    hn = filter(lambda x: x[0] == u'hostname', dhcp_options)
    if hostname:
        try:
            if hn[0][1] != hostname:
                raise RuntimeError(u"Client's hostname doesn't match.")
        except IndexError:
            raise RuntimeError(u"Option list doesn't contain hostname option.")
    else:
        if len(hn) != 0:
            raise RuntimeError(u"Option list contains hostname option.")
    print (u"Option 12 hostname: OK")

    # Option 53
    mt = filter(lambda x: x[0] == u'message-type', dhcp_options)[0][1]
    if mt != 1:
        raise RuntimeError(u"Option 53 message-type error.")
    print (u"Option 53 message-type: OK")

    # Option 55
    prl = filter(lambda x: x[0] == u'param_req_list', dhcp_options)[0][1]
    if prl != u'\x01\x1c\x02\x03\x0f\x06w\x0c,/\x1ay*':
        raise RuntimeError(u"Option 55 param_req_list error.")
    print (u"Option 55 param_req_list: OK")

    # Option 255
    if u'end' not in dhcp_options:
        raise RuntimeError(u"end option error.")
    print (u"end option: OK")

    sys.exit(0)


if __name__ == "__main__":
    main()
