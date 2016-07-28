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
from scapy.layers.inet6 import IPv6, UDP, UDP_SERVICES

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def dhcpv6_solicit(tx_if, rx_if, dhcp_multicast_ip, link_local_ip, proxy_ip,
                   server_ip, server_mac, client_duid, client_mac):
    """Send and check DHCPv6 SOLICIT proxy packet.

    :return interface_id: ID of proxy interface.
    """

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp6_solicit_pkt = Ether(src=client_mac, dst="33:33:00:01:00:02") / \
                        IPv6(src=link_local_ip, dst=dhcp_multicast_ip) / \
                        UDP(sport=UDP_SERVICES.dhcpv6_client,
                            dport=UDP_SERVICES.dhcpv6_server) / \
                        DHCP6_Solicit() / \
                        DHCP6OptClientId(duid=client_duid)

    sent_packets.append(dhcp6_solicit_pkt)
    txq.send(dhcp6_solicit_pkt)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCPv6 SOLICIT timeout')

    if ether.dst != server_mac:
        raise RuntimeError("Destination MAC address error!")
    print "Destination MAC address: OK."

    if ether['IPv6'].src != proxy_ip:
        raise RuntimeError("Source IP address error!")
    print "Source IP address: OK."

    if ether['IPv6'].dst != server_ip:
        raise RuntimeError("Destination IP address error!")
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


def dhcpv6_advertise(rx_if, tx_if, link_local_ip, proxy_ip,
                     server_ip, server_mac, proxy_to_server_mac, interface_id):
    """Send and check DHCPv6 ADVERTISE proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp6_advertise_pkt = Ether(src=server_mac, dst=proxy_to_server_mac) / \
                          IPv6(src=server_ip, dst=proxy_ip) / \
                          UDP(sport=UDP_SERVICES.dhcpv6_server,
                              dport=UDP_SERVICES.dhcpv6_client) / \
                          DHCP6_RelayReply(peeraddr=link_local_ip,
                                           linkaddr=proxy_ip) / \
                          DHCP6OptIfaceId(ifaceid=interface_id) / \
                          DHCP6OptRelayMsg() / \
                          DHCP6_Advertise()

    sent_packets.append(dhcp6_advertise_pkt)
    txq.send(dhcp6_advertise_pkt)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCPv6 ADVERTISE timeout')

    if ether['IPv6'].src != proxy_ip:
        raise RuntimeError("Source IP address error!")
    print "Source IP address: OK."

    if ether['IPv6']['UDP']['Raw'].load != interface_id:
        raise RuntimeError("Interface ID error!")
    print "Interface ID address: OK."


def dhcpv6_request(tx_if, rx_if, dhcp_multicast_ip, link_local_ip, proxy_ip,
                   server_ip, client_duid, client_mac):
    """Send and check DHCPv6 REQUEST proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp6_request_pkt = Ether(src=client_mac, dst="33:33:00:01:00:02") / \
                        IPv6(src=link_local_ip, dst=dhcp_multicast_ip) / \
                        UDP(sport=UDP_SERVICES.dhcpv6_client,
                            dport=UDP_SERVICES.dhcpv6_server) / \
                        DHCP6_Request() / \
                        DHCP6OptClientId(duid=client_duid)

    sent_packets.append(dhcp6_request_pkt)
    txq.send(dhcp6_request_pkt)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCPv6 REQUEST timeout')

    if ether['IPv6'].src != proxy_ip:
        raise RuntimeError("Source IP address error!")
    print "Source IP address: OK."

    if ether['IPv6'].dst != server_ip:
        raise RuntimeError("Destination IP address error!")
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


def dhcpv6_reply(rx_if, tx_if, dhcp_multicast_ip, link_local_ip, proxy_ip,
                 server_ip, server_mac, interface_id):
    """Send and check DHCPv6 REPLY proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp_reply_pkt = Ether(src=server_mac) / \
                    IPv6(src=server_ip, dst=dhcp_multicast_ip) / \
                    UDP(sport=UDP_SERVICES.dhcpv6_server,
                        dport=UDP_SERVICES.dhcpv6_client) / \
                    DHCP6_RelayReply(peeraddr=link_local_ip,
                                     linkaddr=proxy_ip) / \
                    DHCP6OptIfaceId(ifaceid=interface_id) / \
                    DHCP6OptRelayMsg() / \
                    DHCP6_Reply()

    sent_packets.append(dhcp_reply_pkt)
    txq.send(dhcp_reply_pkt)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCPv6 REPLY timeout')

    if ether['IPv6'].src != proxy_ip:
        raise RuntimeError("Source IP address error!")
    print "Source IP address: OK."

    if ether['IPv6']['UDP']['Raw'].load != interface_id:
        raise RuntimeError("Interface ID error!")
    print "Interface ID address: OK."


def main():
    """Send DHCPv6 proxy messages."""

    args = TrafficScriptArg(['tx_src_ip', 'tx_dst_ip', 'proxy_ip', 'proxy_mac',
                             'server_ip', 'client_mac', 'server_mac',
                             'proxy_to_server_mac'])

    client_if = args.get_arg('tx_if')
    server_if = args.get_arg('rx_if')
    proxy_ip = args.get_arg('proxy_ip')
    proxy_mac = args.get_arg('proxy_mac')
    proxy_to_server_mac = args.get_arg('proxy_to_server_mac')
    server_ip = args.get_arg('server_ip')
    client_mac = args.get_arg('client_mac')
    server_mac = args.get_arg('server_mac')

    link_local_ip = "fe80::1"
    dhcp_multicast_ip = "ff02::1:2"
    client_duid = str(random.randint(0, 9999))

    # SOLICIT
    interface_id = dhcpv6_solicit(client_if, server_if, dhcp_multicast_ip,
                                  link_local_ip, proxy_ip, server_ip,
                                  server_mac, client_duid, client_mac)

    # ADVERTISE
    dhcpv6_advertise(client_if, server_if, link_local_ip, proxy_ip,
                     server_ip, server_mac, proxy_to_server_mac, interface_id)

    # REQUEST
    dhcpv6_request(client_if, server_if, dhcp_multicast_ip, link_local_ip,
                   proxy_ip, server_ip, client_duid, client_mac)

    # REPLY
    dhcpv6_reply(client_if, server_if, dhcp_multicast_ip, link_local_ip,
                 proxy_ip, server_ip, server_mac, interface_id)

    sys.exit(0)

if __name__ == "__main__":
    main()
