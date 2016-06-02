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

"""Traffic script that sends a DHCP ACK message when DHCP REQUEST message is
received."""

import sys

from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from scapy.layers.dhcp import BOOTP, DHCP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def is_discover(pkt):
    """If DHCP message type option is set to dhcp discover return True,
    else return False. False is returned also if exception occurs."""
    dhcp_discover = 1
    try:
        dhcp_options = pkt['BOOTP']['DHCP options'].options
        message_type = filter(lambda x: x[0] == 'message-type',
                              dhcp_options)
        message_type = message_type[0][1]
        return message_type == dhcp_discover
    except:
        return False


def main():
    """Main function of the script file."""
    args = TrafficScriptArg(['server_mac', 'server_ip', 'client_ip',
                             'client_mask', 'lease_time'])

    server_if = args.get_arg('rx_if')
    server_mac = args.get_arg('server_mac')
    server_ip = args.get_arg('server_ip')

    client_ip = args.get_arg('client_ip')
    client_mask = args.get_arg('client_mask')
    max_dhcp_discover = 10

    lease_time = int(args.get_arg('lease_time'))

    rxq = RxQueue(server_if)
    txq = TxQueue(server_if)
    sent_packets = []

    for _ in range(10):
        dhcp_discover = rxq.recv(10)
        if is_discover(dhcp_discover):
            break
    else:
        raise RuntimeError("DHCP DISCOVER Rx error.")

    dhcp_offer = Ether(src=server_mac, dst=dhcp_discover.src)
    dhcp_offer /= IP(src=server_ip, dst="255.255.255.255")
    dhcp_offer /= UDP(sport=67, dport=68)
    dhcp_offer /= BOOTP(op=2,
                        xid=dhcp_discover['BOOTP'].xid,
                        yiaddr=client_ip,
                        siaddr=server_ip,
                        chaddr=dhcp_discover['BOOTP'].chaddr)
    dhcp_offer_options = [("message-type", "offer"),  # Option 53
                          ("subnet_mask", client_mask),  # Option 1
                          ("server_id", server_ip),  # Option 54, dhcp server
                          ("lease_time", lease_time),  # Option 51
                          "end"]
    dhcp_offer /= DHCP(options=dhcp_offer_options)

    txq.send(dhcp_offer)
    sent_packets.append(dhcp_offer)

    for _ in range(0, max_dhcp_discover):
        pkt = rxq.recv(5, sent_packets)
        if not pkt:
            raise RuntimeError("DHCP REQUEST Rx timeout.")
        if is_discover(pkt):
            continue
        dhcp_request = pkt
        break
    else:
        raise RuntimeError("Max DHCP DISCOVER messages limit reached.")

    # Send dhcp ack
    dhcp_ack = Ether(src=server_mac, dst=dhcp_request.src)
    dhcp_ack /= IP(src=server_ip, dst="255.255.255.255")
    dhcp_ack /= UDP(sport=67, dport=68)
    dhcp_ack /= BOOTP(op=2,
                      xid=dhcp_request['BOOTP'].xid,
                      yiaddr=client_ip,
                      siaddr=server_ip,
                      flags=dhcp_request['BOOTP'].flags,
                      chaddr=dhcp_request['BOOTP'].chaddr)
    dhcp_ack_options = [("message-type", "ack"),  # Option 53. 5: ACK, 6: NAK
                        ("subnet_mask", client_mask),  # Option 1
                        ("server_id", server_ip),  # Option 54, dhcp server
                        ("lease_time", lease_time),  # Option 51,
                        "end"]
    dhcp_ack /= DHCP(options=dhcp_ack_options)

    txq.send(dhcp_ack)
    sent_packets.append(dhcp_ack)

    sys.exit(0)

if __name__ == "__main__":
    main()
