#!/usr/bin/env python
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the u"License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an u"AS IS" BASIS,
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
    u"""If DHCP message type option is set to dhcp discover return True,
    else return False. False is returned also if exception occurs."""
    dhcp_discover = 1
    try:
        dhcp_options = pkt[u'BOOTP'][u'DHCP options'].options
        message_type = filter(lambda x: x[0] == u'message-type',
                              dhcp_options)
        message_type = message_type[0][1]
        return message_type == dhcp_discover
    except:
        return False


def is_request(pkt):
    u"""If DHCP message type option is DHCP REQUEST return True,
    else return False. False is returned also if exception occurs."""
    dhcp_request = 3
    try:
        dhcp_options = pkt[u'BOOTP'][u'DHCP options'].options
        message_type = filter(lambda x: x[0] == u'message-type',
                              dhcp_options)
        message_type = message_type[0][1]
        return message_type == dhcp_request
    except:
        return False


def main():
    u"""Main function of the script file."""
    args = TrafficScriptArg([u'server_mac', u'server_ip', u'client_ip',
                             u'client_mask', u'lease_time'])

    server_if = args.get_arg(u'rx_if')
    server_mac = args.get_arg(u'server_mac')
    server_ip = args.get_arg(u'server_ip')

    client_ip = args.get_arg(u'client_ip')
    client_mask = args.get_arg(u'client_mask')

    lease_time = int(args.get_arg(u'lease_time'))

    rxq = RxQueue(server_if)
    txq = TxQueue(server_if)
    sent_packets = []

    for _ in range(10):
        dhcp_discover = rxq.recv(10)
        if is_discover(dhcp_discover):
            break
    else:
        raise RuntimeError(u"DHCP DISCOVER Rx error.")

    dhcp_offer = Ether(src=server_mac, dst=dhcp_discover.src)
    dhcp_offer /= IP(src=server_ip, dst=u"255.255.255.255")
    dhcp_offer /= UDP(sport=67, dport=68)
    dhcp_offer /= BOOTP(op=2,
                        xid=dhcp_discover[u'BOOTP'].xid,
                        yiaddr=client_ip,
                        siaddr=server_ip,
                        chaddr=dhcp_discover[u'BOOTP'].chaddr)
    dhcp_offer_options = [(u"message-type", u"offer"),  # Option 53
                          (u"subnet_mask", client_mask),  # Option 1
                          (u"server_id", server_ip),  # Option 54, dhcp server
                          (u"lease_time", lease_time),  # Option 51
                          u"end"]
    dhcp_offer /= DHCP(options=dhcp_offer_options)

    txq.send(dhcp_offer)
    sent_packets.append(dhcp_offer)

    max_other_pkts = 10
    for _ in range(0, max_other_pkts):
        dhcp_request = rxq.recv(5, sent_packets)
        if not dhcp_request:
            raise RuntimeError(u"DHCP REQUEST Rx timeout.")
        if is_request(dhcp_request):
            break
    else:
        raise RuntimeError(u"Max RX packet limit reached.")

    # Send dhcp ack
    dhcp_ack = Ether(src=server_mac, dst=dhcp_request.src)
    dhcp_ack /= IP(src=server_ip, dst=u"255.255.255.255")
    dhcp_ack /= UDP(sport=67, dport=68)
    dhcp_ack /= BOOTP(op=2,
                      xid=dhcp_request[u'BOOTP'].xid,
                      yiaddr=client_ip,
                      siaddr=server_ip,
                      flags=dhcp_request[u'BOOTP'].flags,
                      chaddr=dhcp_request[u'BOOTP'].chaddr)
    dhcp_ack_options = [(u"message-type", u"ack"),  # Option 53. 5: ACK, 6: NAK
                        (u"subnet_mask", client_mask),  # Option 1
                        (u"server_id", server_ip),  # Option 54, dhcp server
                        (u"lease_time", lease_time),  # Option 51,
                        u"end"]
    dhcp_ack /= DHCP(options=dhcp_ack_options)

    txq.send(dhcp_ack)
    sent_packets.append(dhcp_ack)

    sys.exit(0)

if __name__ == "__main__":
    main()
