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

from scapy.layers.inet import UDP_SERVICES
from scapy.all import Ether, IP, DHCP, UDP, BOOTP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def is_discover(pkt):
    dhcp_discover = 1
    if pkt.haslayer("DHCP"):
        dhcp_options = pkt['DHCP options'].options
        message_type = filter(lambda x: x[0] == 'message-type', dhcp_options)[0][1]
        return message_type == dhcp_discover
    else:
        return False


def main():
    args = TrafficScriptArg(['client_mac', 'server_mac', 'server_ip',
                             'client_ip', 'client_mask'],
                            ['hostname', 'offer_xid'])

    server_if = args.get_arg('rx_if')
    server_mac = args.get_arg('server_mac')
    server_ip = args.get_arg('server_ip')

    client_mac = args.get_arg('client_mac')
    client_ip = args.get_arg('client_ip')
    client_mask = args.get_arg('client_mask')

    hostname = args.get_arg('hostname')
    offer_xid = args.get_arg('offer_xid')

    rx_src_ip = '0.0.0.0'
    rx_dst_ip = '255.255.255.255'

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
                        xid=int(offer_xid) if offer_xid
                        else dhcp_discover['BOOTP'].xid,
                        yiaddr=client_ip,
                        siaddr=server_ip,
                        chaddr=dhcp_discover['BOOTP'].chaddr)
    dhcp_offer_options = [("message-type", "offer"),  # Option 53
                          ("subnet_mask", client_mask),  # Option 1
                          # ("router", client_router),     # Option 3
                          ("server_id", server_ip),  # Option 54, dhcp server
                          ("lease_time", 43200),  # Option 51
                          "end"]
    dhcp_offer /= DHCP(options=dhcp_offer_options)

    txq.send(dhcp_offer)
    sent_packets.append(dhcp_offer)

    max_dhcp_discover = 10
    for _ in range(0, max_dhcp_discover):
        pkt = rxq.recv(2, sent_packets)
        try:
            if is_discover(pkt):
                continue
        except AttributeError:
            raise RuntimeError("DHCP REQUEST Rx timeout.")
        dhcp_request = pkt
        break
    else:
        raise RuntimeError("DHCP REQUEST Rx timeout.")

    if offer_xid:
        raise RuntimeError("DHCP REQUEST received.")

    # CHECK ETHER, IP, UDP
    if dhcp_request.dst != dhcp_discover.dst:
        raise RuntimeError("Destination MAC error.")
    print "Destination MAC: OK."

    if dhcp_request.src != dhcp_discover.src:
        raise RuntimeError("Source MAC error.")
    print "Source MAC: OK."

    if dhcp_request['IP'].dst != rx_dst_ip:
        raise RuntimeError("Destination IP error.")
    print "Destination IP: OK."

    if dhcp_request['IP'].src != rx_src_ip:
        raise RuntimeError("Source IP error.")
    print "Source IP: OK."

    if dhcp_request['IP']['UDP'].dport != UDP_SERVICES.bootps:
        raise RuntimeError("BOOTPs error.")
    print "BOOTPs: OK."

    if dhcp_request['IP']['UDP'].sport != UDP_SERVICES.bootpc:
        raise RuntimeError("BOOTPc error.")
    print "BOOTPc: OK."

    # CHECK BOOTP
    if dhcp_request['BOOTP'].op != dhcp_discover['BOOTP'].op:
        raise RuntimeError(" error.")
    print " : OK"

    if dhcp_request['BOOTP'].xid != dhcp_discover['BOOTP'].xid:
        raise RuntimeError(" error.")
    print " : OK"

    if dhcp_request['BOOTP'].ciaddr != '0.0.0.0':
        raise RuntimeError("BOOTP ciaddr error.")
    print "BOOTP ciaddr: OK"

    ca = dhcp_request['BOOTP'].chaddr[:dhcp_request['BOOTP'].hlen].encode('hex')
    if ca != client_mac.replace(':', ''):
        raise RuntimeError("BOOTP client hardware address error.")
    print "BOOTP client hardware address: OK"

    if dhcp_request['BOOTP'].options != dhcp_discover['BOOTP'].options:
        raise RuntimeError(" error.")
    print " : OK"

    # CHECK DHCP OPTIONS
    dhcp_options = dhcp_request['DHCP options'].options

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

    # Option 50
    ra = filter(lambda x: x[0] == 'requested_addr', dhcp_options)[0][1]
    if ra != client_ip:
        raise RuntimeError("Option 50 requested_addr error.")
    print "Option 50 requested_addr: OK"

    # Option 53
    mt = filter(lambda x: x[0] == 'message-type', dhcp_options)[0][1]
    if mt != 3:  # request
        raise RuntimeError("Option 53 message-type error.")
    print "Option 53 message-type: OK"

    # Option 54
    sid = filter(lambda x: x[0] == 'server_id', dhcp_options)[0][1]
    if sid != server_ip:
        raise RuntimeError("Option 54 server_id error.")
    print "Option 54 server_id: OK"

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
