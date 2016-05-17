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

from robot.api import logger
from scapy.layers.inet import UDP_SERVICES

from resources.libraries.python.PacketVerifier import RxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    args = TrafficScriptArg(
        ['rx_src_mac', ])

    rx_if = args.get_arg('rx_if')
    rx_src_mac = args.get_arg('rx_src_mac')

    rx_dst_mac = 'ff:ff:ff:ff:ff:ff'
    rx_src_ip = '0.0.0.0'
    rx_dst_ip = '255.255.255.255'
    BOOTREQUEST = 1
    dhcpmagic = 'c\x82Sc'

    rxq = RxQueue(rx_if)

    ether = rxq.recv(10)

    if ether is None:
        raise RuntimeError("DHCP DISCOVER Rx timeout.")

    if ether.dst != rx_dst_mac:
        raise RuntimeError("Dst MAC error.")
    logger.debug("Dst MAC: OK.")

    if ether.src != rx_src_mac:
        raise RuntimeError("Src MAC error.")
    logger.debug("Src MAC: OK.")

    if ether['IP'].dst != rx_dst_ip or ether['IP'].src != rx_src_ip:
        raise RuntimeError("IP error.")
    logger.debug("IP: OK.")

    if ether['IP']['UDP'].dport != UDP_SERVICES.bootps:
        raise RuntimeError("BOOTPs error.")
    logger.debug("BOOTPs: OK.")

    if ether['IP']['UDP'].sport != UDP_SERVICES.bootpc:
        raise RuntimeError("BOOTPc error.")
    logger.debug("BOOTPc: OK.")

    bootp = ether['BOOTP']

    if bootp.op != BOOTREQUEST:
        raise RuntimeError("BOOTP error.")
    logger.debug("BOOTP: OK")

    if bootp.ciaddr != '0.0.0.0':
        raise RuntimeError("BOOTP error.")
    logger.debug("BOOTP: OK")

    if bootp.yiaddr != '0.0.0.0':
        raise RuntimeError("BOOTP error.")
    logger.debug("BOOTP: OK")

    if bootp.siaddr != '0.0.0.0':
        raise RuntimeError("BOOTP error.")
    logger.debug("BOOTP: OK")

    if bootp.giaddr != '0.0.0.0':
        raise RuntimeError("BOOTP error.")
    logger.debug("BOOTP: OK")

    chaddr = bootp.chaddr[:bootp.hlen].encode('hex')
    if chaddr != rx_src_mac.replace(':', ''):
        raise RuntimeError("BOOTP client hardware address error.")
    logger.debug("BOOTP client hardware address: OK")

    # Check hostname

    # Check bootfile

    # Check bootp magic
    if bootp.options != dhcpmagic:
        raise RuntimeError("DHCP magic error.")
    logger.debug("DHCP magic: OK")

    # Check options
    dhcp_options = ether['DHCP options'].options

    mt = filter(lambda x: x[0] == 'message-type', dhcp_options)[0][1]
    if mt != 1:
        raise RuntimeError("message-type error.")
    logger.debug("message-type: OK")

    prl = filter(lambda x: x[0] == 'param_req_list', dhcp_options)[0][1]
    if prl != '\x01\x1c\x02\x03\x0f\x06w\x0c,/\x1ay*':
        raise RuntimeError("param_req_list error.")
    logger.debug("param_req_list: OK")

    if 'end' not in dhcp_options:
        raise RuntimeError("end option error.")
    logger.debug("end option: OK")

    sys.exit(0)


if __name__ == "__main__":
    main()
