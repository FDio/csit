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

"""Traffic script that sends an DHCP OFFER message and checks if the DHCP
REQUEST contains all required fields."""

import sys

from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP, UDP_SERVICES
from scapy.layers.dhcp import BOOTP, DHCP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def is_discover(pkt):
    """If DHCP message type option is set to dhcp discover return True,
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
    """If DHCP message type option is DHCP REQUEST return True,
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
    """Main function of the script file."""
    args = TrafficScriptArg([u'client_mac', u'server_mac', u'server_ip',
                             u'client_ip', u'client_mask'],
                            [u'hostname', u'offer_xid'])

    server_if = args.get_arg(u'rx_if')
    server_mac = args.get_arg(u'server_mac')
    server_ip = args.get_arg(u'server_ip')

    client_mac = args.get_arg(u'client_mac')
    client_ip = args.get_arg(u'client_ip')
    client_mask = args.get_arg(u'client_mask')

    hostname = args.get_arg(u'hostname')
    offer_xid = args.get_arg(u'offer_xid')

    rx_src_ip = u'0.0.0.0'
    rx_dst_ip = u'255.255.255.255'

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
    dhcp_offer /= IP(src=server_ip, dst="255.255.255.255")
    dhcp_offer /= UDP(sport=67, dport=68)
    dhcp_offer /= BOOTP(op=2,
                        # if offer_xid differs from xid value in DHCP DISCOVER
                        # the DHCP OFFER has to be discarded
                        xid=int(offer_xid) if offer_xid
                        else dhcp_discover[u'BOOTP'].xid,
                        yiaddr=client_ip,
                        siaddr=server_ip,
                        chaddr=dhcp_discover[u'BOOTP'].chaddr)
    dhcp_offer_options = [(u"message-type", u"offer"),  # Option 53
                          (u"subnet_mask", client_mask),  # Option 1
                          (u"server_id", server_ip),  # Option 54, dhcp server
                          (u"lease_time", 43200),  # Option 51
                          "end"]
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

    if offer_xid:
        # if offer_xid differs from xid value in DHCP DISCOVER the DHCP OFFER
        # has to be discarded
        raise RuntimeError(f"DHCP REQUEST received. DHCP OFFER with wrong XID "
                           f"has not been discarded.")

    # CHECK ETHER, IP, UDP
    if dhcp_request.dst != dhcp_discover.dst:
        raise RuntimeError(u"Destination MAC error.")
    print (f"Destination MAC: OK.")

    if dhcp_request.src != dhcp_discover.src:
        raise RuntimeError(u"Source MAC error.")
    print (f"Source MAC: OK.")

    if dhcp_request[u'IP'].dst != rx_dst_ip:
        raise RuntimeError(u"Destination IP error.")
    print (f"Destination IP: OK.")

    if dhcp_request[u'IP'].src != rx_src_ip:
        raise RuntimeError(u"Source IP error.")
    print (f"Source IP: OK.")

    if dhcp_request[u'IP'][u'UDP'].dport != UDP_SERVICES.bootps:
        raise RuntimeError(u"BOOTPs error.")
    print (f"BOOTPs: OK.")

    if dhcp_request[u'IP'][u'UDP'].sport != UDP_SERVICES.bootpc:
        raise RuntimeError(u"BOOTPc error.")
    print (f"BOOTPc: OK.")

    # CHECK BOOTP
    if dhcp_request[u'BOOTP'].op != dhcp_discover[u'BOOTP'].op:
        raise RuntimeError(u"BOOTP operation error.")
    print (f"BOOTP operation: OK")

    if dhcp_request[u'BOOTP'].xid != dhcp_discover[u'BOOTP'].xid:
        raise RuntimeError(u"BOOTP XID error.")
    print (f"BOOTP XID: OK")

    if dhcp_request[u'BOOTP'].ciaddr != u'0.0.0.0':
        raise RuntimeError(u"BOOTP ciaddr error.")
    print (f"BOOTP ciaddr: OK")

    ca = dhcp_request[u'BOOTP'].chaddr[:dhcp_request[u'BOOTP'].hlen].encode(u'hex')
    if ca != client_mac.replace(u':', u''):
        raise RuntimeError(u"BOOTP client hardware address error.")
    print (f"BOOTP client hardware address: OK")

    if dhcp_request[u'BOOTP'].options != dhcp_discover[u'BOOTP'].options:
        raise RuntimeError(u"DHCP options error.")
    print (f"DHCP options: OK")

    # CHECK DHCP OPTIONS
    dhcp_options = dhcp_request[u'DHCP options'].options

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
    print (f"Option 12 hostname: OK")

    # Option 50
    ra = filter(lambda x: x[0] == u'requested_addr', dhcp_options)[0][1]
    if ra != client_ip:
        raise RuntimeError(u"Option 50 requested_addr error.")
    print (f"Option 50 requested_addr: OK")

    # Option 53
    mt = filter(lambda x: x[0] == u'message-type', dhcp_options)[0][1]
    if mt != 3:  # request
        raise RuntimeError(u"Option 53 message-type error.")
    print (f"Option 53 message-type: OK")

    # Option 54
    sid = filter(lambda x: x[0] == u'server_id', dhcp_options)[0][1]
    if sid != server_ip:
        raise RuntimeError(u"Option 54 server_id error.")
    print (f"Option 54 server_id: OK")

    # Option 55
    prl = filter(lambda x: x[0] == u'param_req_list', dhcp_options)[0][1]
    if prl != u'\x01\x1c\x02\x03\x0f\x06w\x0c,/\x1ay*':
        raise RuntimeError(u"Option 55 param_req_list error.")
    print (f"Option 55 param_req_list: OK")

    # Option 255
    if u'end' not in dhcp_options:
        raise RuntimeError(u"end option error.")
    print (f"end option: OK")

    sys.exit(0)

if __name__ == "__main__":
    main()
