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

"""Traffic script that sends an DHCP OFFER message and checks if the DHCP
REQUEST contains all required fields."""

import sys

from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP, UDP_SERVICES
from scapy.layers.dhcp import BOOTP, DHCP

from ..PacketVerifier import RxQueue, TxQueue
from ..TrafficScriptArg import TrafficScriptArg


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


def is_request(pkt):
    """If DHCP message type option is DHCP REQUEST return True,
    else return False. False is returned also if exception occurs."""
    dhcp_request = 3
    try:
        dhcp_options = pkt['BOOTP']['DHCP options'].options
        message_type = filter(lambda x: x[0] == 'message-type',
                              dhcp_options)
        message_type = message_type[0][1]
        return message_type == dhcp_request
    except:
        return False


def main():
    """Main function of the script file."""
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
                        # if offer_xid differs from xid value in DHCP DISCOVER
                        # the DHCP OFFER has to be discarded
                        xid=int(offer_xid) if offer_xid
                        else dhcp_discover['BOOTP'].xid,
                        yiaddr=client_ip,
                        siaddr=server_ip,
                        chaddr=dhcp_discover['BOOTP'].chaddr)
    dhcp_offer_options = [("message-type", "offer"),  # Option 53
                          ("subnet_mask", client_mask),  # Option 1
                          ("server_id", server_ip),  # Option 54, dhcp server
                          ("lease_time", 43200),  # Option 51
                          "end"]
    dhcp_offer /= DHCP(options=dhcp_offer_options)

    txq.send(dhcp_offer)
    sent_packets.append(dhcp_offer)

    max_other_pkts = 10
    for _ in range(0, max_other_pkts):
        dhcp_request = rxq.recv(5, sent_packets)
        if not dhcp_request:
            raise RuntimeError("DHCP REQUEST Rx timeout.")
        if is_request(dhcp_request):
            break
    else:
        raise RuntimeError("Max RX packet limit reached.")

    if offer_xid:
        # if offer_xid differs from xid value in DHCP DISCOVER the DHCP OFFER
        # has to be discarded
        raise RuntimeError("DHCP REQUEST received. DHCP OFFER with wrong XID "
                           "has not been discarded.")

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
        raise RuntimeError("BOOTP operation error.")
    print "BOOTP operation: OK"

    if dhcp_request['BOOTP'].xid != dhcp_discover['BOOTP'].xid:
        raise RuntimeError("BOOTP XID error.")
    print "BOOTP XID: OK"

    if dhcp_request['BOOTP'].ciaddr != '0.0.0.0':
        raise RuntimeError("BOOTP ciaddr error.")
    print "BOOTP ciaddr: OK"

    ca = dhcp_request['BOOTP'].chaddr[:dhcp_request['BOOTP'].hlen].encode('hex')
    if ca != client_mac.replace(':', ''):
        raise RuntimeError("BOOTP client hardware address error.")
    print "BOOTP client hardware address: OK"

    if dhcp_request['BOOTP'].options != dhcp_discover['BOOTP'].options:
        raise RuntimeError("DHCP options error.")
    print "DHCP options: OK"

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
