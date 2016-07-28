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

"""Traffic script that sends DHCPv6 proxy packets."""

from scapy.layers.dhcp6 import *

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def solicit(tx_if, rx_if, dhcp_multicast_ip, proxy_ip, server_ip, client_duid):
    """Send and check DHCPv6 SOLICIT proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp_solicit = Ether() / \
                   IPv6(dst=dhcp_multicast_ip) / \
                   UDP(sport=546, dport=547) / \
                   DHCP6_Solicit() / \
                   DHCP6OptClientId(duid=client_duid)

    sent_packets.append(dhcp_solicit)
    txq.send(dhcp_solicit)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCP SOLICIT timeout')

    if ether['IPv6'].src != proxy_ip:
        raise RuntimeError("Source IP address error!")
    print "Source IP address: OK."

    if ether['IPv6'].dst != server_ip:
        raise RuntimeError("Destiination IP address error!")
    print "Destination IP address: OK."

    if ether['IPv6']['UDP']\
        ['DHCPv6 Relay Forward Message (Relay Agent/Server Message)']:
        print "Relay Agent/Server Message: OK."
    else:
        raise RuntimeError("Relay Agent/Server Message error.")

    if ether['IPv6']['UDP']\
        ['DHCPv6 Relay Forward Message (Relay Agent/Server Message)']\
        .linkaddr != proxy_ip:
        raise RuntimeError("Proxy IP address error!")
    print "Proxy IP address: OK."

    try:
        interface_id =  ether['IPv6']['UDP']\
            ['DHCPv6 Relay Forward Message (Relay Agent/Server Message)']\
            ['Unknown DHCPv6 OPtion']['DHCP6 Interface-Id Option'].ifaceid
    except Exception:
        raise RuntimeError("DHCP6 Interface-Id error!")

    return interface_id


def advertise(rx_if, tx_if, dhcp_multicast_ip, proxy_ip,
              server_ip, interface_id):
    """Send and check DHCPv6 ADVERTISE proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp_advertise = Ether() / \
                     IPv6(src=server_ip, dst=dhcp_multicast_ip) / \
                     UDP(sport=547, dport=546) / \
                     DHCP6_RelayReply() / \
                     DHCP6OptIfaceId(ifaceid=interface_id) / \
                     DHCP6OptRelayMsg() / \
                     DHCP6_Advertise()

    sent_packets.append(dhcp_advertise)
    txq.send(dhcp_advertise)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCP ADVERTISE timeout')

    if ether['IPv6'].src != proxy_ip:
        raise RuntimeError("Source IP address error!")
    print "Source IP address: OK."


def request(tx_if, rx_if, dhcp_multicast_ip, proxy_ip, server_ip, client_duid):
    """Send and check DHCPv6 REQUEST proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp_request = Ether() / \
                   IPv6(dst=dhcp_multicast_ip) / \
                   UDP(sport=546, dport=547) / \
                   DHCP6_Request() / \
                   DHCP6OptClientId(duid=client_duid)

    sent_packets.append(dhcp_request)
    txq.send(dhcp_request)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCP REQUEST timeout')

    if ether is None:
        raise RuntimeError('DHCP SOLICIT timeout')

    if ether['IPv6'].src != proxy_ip:
        raise RuntimeError("Source IP address error!")
    print "Source IP address: OK."

    if ether['IPv6'].dst != server_ip:
        raise RuntimeError("Destiination IP address error!")
    print "Destination IP address: OK."

    if ether['IPv6']['UDP']\
        ['DHCPv6 Relay Forward Message (Relay Agent/Server Message)']:
        print "Relay Agent/Server Message: OK."
    else:
        raise RuntimeError("Relay Agent/Server Message error.")

    if ether['IPv6']['UDP']\
            ['DHCPv6 Relay Forward Message (Relay Agent/Server Message)']\
            .linkaddr != proxy_ip:
        raise RuntimeError("Proxy IP address error!")
    print "Proxy IP address: OK."


def reply(rx_if, tx_if, dhcp_multicast_ip, proxy_ip, server_ip, interface_id):
    """Send and check DHCPv6 REPLY proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp_reply = Ether() / \
                 IPv6(src=server_ip, dst=dhcp_multicast_ip) / \
                 UDP(sport=547, dport=546) / \
                 DHCP6_RelayReply() / \
                 DHCP6OptIfaceId(ifaceid=interface_id) / \
                 DHCP6OptRelayMsg() / \
                 DHCP6_Reply()

    sent_packets.append(dhcp_reply)
    txq.send(dhcp_reply)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCP REPLY timeout')

    if ether['IPv6'].src != proxy_ip:
        raise RuntimeError("Source IP address error!")
    print "Source IP address: OK."


def main():
    """Send DHCPv6 proxy messages."""

    args = TrafficScriptArg(['tx_src_ip', 'tx_dst_ip', 'proxy_ip', 'server_ip'])

    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    proxy_ip = args.get_arg('proxy_ip')
    server_ip = args.get_arg('server_ip')

    dhcp_multicast_ip = "ff02::1:2"
    client_duid = duid=str(random.randint(0, 9999))

    # SOLICIT
    interface_id = solicit(tx_if, rx_if, dhcp_multicast_ip, proxy_ip, server_ip,
                           client_duid)

    # ADVERTISE
    advertise(tx_if, rx_if, dhcp_multicast_ip, proxy_ip, server_ip,
              interface_id)

    # REQUEST
    request(tx_if, rx_if, dhcp_multicast_ip, proxy_ip, server_ip, client_duid)

    # REPLY
    reply(tx_if, rx_if, dhcp_multicast_ip, proxy_ip, server_ip, interface_id)

    sys.exit(0)

if __name__ == "__main__":
    main()
