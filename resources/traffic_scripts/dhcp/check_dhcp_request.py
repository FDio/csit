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

"""Traffic script that sends an ..."""

import sys

from robot.api import logger
from scapy.layers.inet import UDP_SERVICES
from scapy.all import Ether, IP, DHCP, UDP, BOOTP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def is_discover(pkt):
    DHCP_DISCOVER = 1
    dhcp_options = pkt['DHCP options'].options
    message_type = filter(lambda x: x[0] == 'message-type', dhcp_options)[0][1]
    return message_type == DHCP_DISCOVER


#
# def main():
#     args = TrafficScriptArg(
#         ['rx_src_mac', ])
#
#     rx_if = args.get_arg('rx_if')
#     rx_src_mac = args.get_arg('rx_src_mac')

# Check dhcp discover
# Send dhcp offer
## Save mac from discover
## Create offer
# Receive request filter dhcp discover
# Check dhcp request


server_if = 'eth3'
server_mac = '08:00:27:58:71:eb'
server_ip = '192.168.26.5'

client_mac = '08:00:27:66:b8:57'
client_ip = '192.168.26.128'
client_mask = '255.255.255.0'
client_router = '192.168.26.1'


rxq = RxQueue(server_if)
txq = TxQueue(server_if)
sent_packets = []


dhcp_discover = rxq.recv(10)

if not is_discover(dhcp_discover):
    raise RuntimeError("DHCP DISCOVER Rx error.")

dhcp_offer = Ether(src=server_mac, dst=dhcp_discover.src)
dhcp_offer /= IP(src=server_ip, dst="255.255.255.255")
dhcp_offer /= UDP(sport=67, dport=68)
dhcp_offer /= BOOTP(op=2,
                    xid=dhcp_discover['BOOTP'].xid,
                    yiaddr=client_ip,
                    siaddr=server_ip,
                    chaddr=dhcp_discover['BOOTP'].chaddr)
dhcp_offer_options = [("message-type", "offer"),     # Option 53
                      ("subnet_mask", client_mask),  # Option 1
                     # ("router", client_router),     # Option 3
                      ("server_id", server_ip),      # Option 54, dhcp server
                      ("lease_time", 43200),         # Option 51
                      "end"]
dhcp_offer /= DHCP(options=dhcp_offer_options)





sys.exit(0)

#
# if __name__ == "__main__":
#     main()
