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

import scapy.layers.inet6  # pylint: disable=unused-import
from scapy.layers.dhcp6 import *
from scapy.layers.inet6 import IPv6, UDP, UDP_SERVICES

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def _check_udp_checksum(pkt):
    """Check udp checksum in ip packet.
    Return true if checksum is correct."""
    new = pkt.__class__(str(pkt))
    del new['UDP'].chksum
    new = new.__class__(str(new))
    return new['UDP'].chksum == pkt['UDP'].chksum


def _get_dhcpv6_msgtype(msg_index):
    """Return DHCPv6 message type string.

    :param msg_index: Index of message type.
    :return: Message type.
    :type msg_index: int
    :rtype msg_str: str
    """
    dhcp6_messages = {
        1: "SOLICIT",
        2: "ADVERTISE",
        3: "REQUEST",
        4: "CONFIRM",
        5: "RENEW",
        6: "REBIND",
        7: "REPLY",
        8: "RELEASE",
        9: "DECLINE",
        10: "RECONFIGURE",
        11: "INFORMATION-REQUEST",
        12: "RELAY-FORW",
        13: "RELAY-REPL"
    }
    return dhcp6_messages[msg_index]


def dhcpv6_solicit(tx_if, rx_if, dhcp_multicast_ip, link_local_ip, proxy_ip,
                   server_ip, server_mac, client_duid, client_mac):
    """Send and check DHCPv6 SOLICIT proxy packet.

    :param tx_if: Client interface.
    :param rx_if: DHCPv6 server interface.
    :param dhcp_multicast_ip: Servers and relay agents multicast address.
    :param link_local_ip: Client link-local address.
    :param proxy_ip: IP address of DHCPv6 proxy server.
    :param server_ip: IP address of DHCPv6 server.
    :param server_mac: MAC address of DHCPv6 server.
    :param client_duid: Client DHCP Unique Identifier.
    :param client_mac: Client MAC address.
    :type tx_if: str
    :type rx_if: str
    :type dhcp_multicast_ip: str
    :type link_local_ip: str
    :type proxy_ip: str
    :type server_ip: str
    :type server_mac: str
    :type client_duid: str
    :type client_mac: str
    :return interface_id: ID of proxy interface.
    :rtype interface_id: str
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
        raise RuntimeError("Destination MAC address error: {} != {}".format(
            ether.dst, server_mac))
    print "Destination MAC address: OK."

    if ether['IPv6'].src != proxy_ip:
        raise RuntimeError("Source IP address error: {} != {}".format(
            ether['IPv6'].src, proxy_ip))
    print "Source IP address: OK."

    if ether['IPv6'].dst != server_ip:
        raise RuntimeError("Destination IP address error: {} != {}".format(
            ether['IPv6'].dst, server_ip))
    print "Destination IP address: OK."

    msgtype = _get_dhcpv6_msgtype(ether['IPv6']['UDP']
        ['DHCPv6 Relay Forward Message (Relay Agent/Server Message)'].msgtype)
    if msgtype != 'RELAY-FORW':
        raise RuntimeError("Message type error: {} != RELAY-FORW".format(
            msgtype))
    print "Message type: OK."

    linkaddr = ether['IPv6']['UDP']\
        ['DHCPv6 Relay Forward Message (Relay Agent/Server Message)'].linkaddr
    if linkaddr != proxy_ip:
        raise RuntimeError("Proxy IP address error: {} != {}".format(
           linkaddr, proxy_ip))
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
    """Send and check DHCPv6 ADVERTISE proxy packet.

    :param rx_if: DHCPv6 server interface.
    :param tx_if: Client interface.
    :param link_local_ip: Client link-local address.
    :param proxy_ip: IP address of DHCPv6 proxy server.
    :param server_ip: IP address of DHCPv6 server.
    :param server_mac: MAC address of DHCPv6 server.
    :param proxy_to_server_mac: MAC address of DHCPv6 proxy interface.
    :param interface_id: ID of proxy interface.
    :type rx_if: str
    :type tx_if: str
    :type link_local_ip: str
    :type proxy_ip: str
    :type server_ip: str
    :type server_mac: str
    :type proxy_to_server_mac: str
    :type interface_id: str
    """

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
        raise RuntimeError("Source IP address error: {} != {}".format(
            ether['IPv6'].src, proxy_ip))
    print "Source IP address: OK."

    if not _check_udp_checksum(ether['IPv6']):
        raise RuntimeError("Checksum error!")
    print "Checksum: OK."

    msgtype = _get_dhcpv6_msgtype(ether['IPv6']['UDP']
                                  ['DHCPv6 Advertise Message'].msgtype)
    if msgtype != 'ADVERTISE':
        raise RuntimeError("Message type error: {} != ADVERTISE".format(
            msgtype))
    print "Message type: OK."


def dhcpv6_request(tx_if, rx_if, dhcp_multicast_ip, link_local_ip, proxy_ip,
                   server_ip, client_duid, client_mac):
    """Send and check DHCPv6 REQUEST proxy packet.

    :param tx_if: Client interface.
    :param rx_if: DHCPv6 server interface.
    :param dhcp_multicast_ip: Servers and relay agents multicast address.
    :param link_local_ip: Client link-local address.
    :param proxy_ip: IP address of DHCPv6 proxy server.
    :param server_ip: IP address of DHCPv6 server.
    :param client_duid: Client DHCP Unique Identifier.
    :param client_mac: Client MAC address.
    :type tx_if: str
    :type rx_if: str
    :type dhcp_multicast_ip: str
    :type link_local_ip: str
    :type proxy_ip: str
    :type server_ip: str
    :type client_duid: str
    :type client_mac: str
    """

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
        raise RuntimeError("Source IP address error: {} != {}".format(
            ether['IPv6'].src, proxy_ip))
    print "Source IP address: OK."

    if ether['IPv6'].dst != server_ip:
        raise RuntimeError("Destination IP address error: {} != {}".format(
            ether['IPv6'].dst, server_ip))
    print "Destination IP address: OK."

    msgtype = _get_dhcpv6_msgtype(ether['IPv6']['UDP']
        ['DHCPv6 Relay Forward Message (Relay Agent/Server Message)'].msgtype)
    if msgtype != 'RELAY-FORW':
        raise RuntimeError("Message type error: {} != RELAY-FORW".format(
            msgtype))
    print "Message type: OK."

    linkaddr = ether['IPv6']['UDP']\
        ['DHCPv6 Relay Forward Message (Relay Agent/Server Message)'].linkaddr
    if linkaddr != proxy_ip:
        raise RuntimeError("Proxy IP address error: {} != {}".format(
           linkaddr, proxy_ip))
    print "Proxy IP address: OK."


def dhcpv6_reply(rx_if, tx_if, link_local_ip, proxy_ip, server_ip, server_mac,
                 interface_id):
    """Send and check DHCPv6 REPLY proxy packet.

    :param rx_if: DHCPv6 server interface.
    :param tx_if: Client interface.
    :param link_local_ip: Client link-local address.
    :param proxy_ip: IP address of DHCPv6 proxy server.
    :param server_ip: IP address of DHCPv6 server.
    :param server_mac: MAC address of DHCPv6 server.
    :param interface_id: ID of proxy interface.
    :type rx_if: str
    :type tx_if: str
    :type link_local_ip: str
    :type proxy_ip: str
    :type server_ip: str
    :type server_mac: str
    :type interface_id: str
    """

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp_reply_pkt = Ether(src=server_mac) / \
                    IPv6(src=server_ip, dst=proxy_ip) / \
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
        raise RuntimeError("Source IP address error: {} != {}".format(
            ether['IPv6'].src, proxy_ip))
    print "Source IP address: OK."

    if not _check_udp_checksum(ether['IPv6']):
        raise RuntimeError("Checksum error!")
    print "Checksum: OK."

    msgtype = _get_dhcpv6_msgtype(ether['IPv6']['UDP']
                                  ['DHCPv6 Reply Message'].msgtype)
    if msgtype != 'REPLY':
        raise RuntimeError("Message type error: {} != REPLY".format(msgtype))
    print "Message type: OK."


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
    dhcpv6_reply(client_if, server_if, link_local_ip, proxy_ip, server_ip,
                 server_mac, interface_id)

    sys.exit(0)

if __name__ == "__main__":
    main()
