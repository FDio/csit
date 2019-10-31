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

"""Traffic script for IPsec verification."""

import sys
import logging

# pylint: disable=no-name-in-module
# pylint: disable=import-error
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.all import Ether
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.layers.ipsec import SecurityAssociation, ESP
from ipaddress import ip_address

from .TrafficScriptArg import TrafficScriptArg
from .PacketVerifier import RxQueue, TxQueue


def check_ipsec(pkt_recv, ip_layer, dst_tun, src_ip, dst_ip, sa_in):
    """Check received IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param ip_layer: Scapy IP layer.
    :param dst_tun: IPsec tunnel destination address.
    :param src_ip: Source IP/IPv6 address of original IP/IPv6 packet.
    :param dst_ip: Destination IP/IPv6 address of original IP/IPv6 packet.
    :param sa_in: IPsec SA for packet decryption.
    :type pkt_recv: scapy.Ether
    :type ip_layer: scapy.layers.inet.IP or scapy.layers.inet6.IPv6
    :type dst_tun: str
    :type src_ip: str
    :type dst_ip: str
    :type sa_in: scapy.layers.ipsec.SecurityAssociation
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(ip_layer):
        raise RuntimeError('Not an {ip} packet received: {pkt}'.format(
            ip=ip_layer.name, pkt=pkt_recv.__repr__()))

    if pkt_recv[ip_layer.name].dst != dst_tun:
        raise RuntimeError(
            'Received packet has invalid destination address: {rec_ip} '
            'should be: {exp_ip}'.format(
                rec_ip=pkt_recv[ip_layer.name].dst, exp_ip=dst_tun))

    if not pkt_recv.haslayer(ESP):
        raise RuntimeError(
            'Not an ESP packet received: {pkt}'.format(pkt=pkt_recv.__repr__()))

    ip_pkt = pkt_recv[ip_layer]
    d_pkt = sa_in.decrypt(ip_pkt)

    if d_pkt[ip_layer].dst != dst_ip:
        raise RuntimeError(
            'Decrypted packet has invalid destination address: {rec_ip} '
            'should be: {exp_ip}'.format(
                rec_ip=d_pkt[ip_layer].dst, exp_ip=dst_ip))

    if d_pkt[ip_layer].src != src_ip:
        raise RuntimeError(
            'Decrypted packet has invalid source address: {rec_ip} should be: '
            '{exp_ip}'.format(rec_ip=d_pkt[ip_layer].src, exp_ip=src_ip))

    if ip_layer == IP and d_pkt[ip_layer.name].proto != 61:
        raise RuntimeError(
            'Decrypted packet has invalid IP protocol: {rec_proto} '
            'should be: 61'.format(rec_proto=d_pkt[ip_layer.name].proto))


def check_ip(pkt_recv, ip_layer, src_ip, dst_ip):
    """Check received IP/IPv6 packet.

    :param pkt_recv: Received packet to verify.
    :param ip_layer: Scapy IP layer.
    :param src_ip: Source IP/IPv6 address.
    :param dst_ip: Destination IP/IPv6 address.
    :type pkt_recv: scapy.Ether
    :type ip_layer: scapy.layers.inet.IP or scapy.layers.inet6.IPv6
    :type src_ip: str
    :type dst_ip: str
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(ip_layer):
        raise RuntimeError('Not an {ip} packet received: {pkt}'.format(
            ip=ip_layer.name, pkt=pkt_recv.__repr__()))

    if pkt_recv[ip_layer.name].dst != dst_ip:
        raise RuntimeError(
            'Received packet has invalid destination address: {rec_ip} '
            'should be: {exp_ip}'.format(
                rec_ip=pkt_recv[ip_layer.name].dst, exp_ip=dst_ip))

    if pkt_recv[ip_layer.name].src != src_ip:
        raise RuntimeError(
            'Received packet has invalid destination address: {rec_ip} '
            'should be: {exp_ip}'.format(
                rec_ip=pkt_recv[ip_layer.name].dst, exp_ip=src_ip))

    if ip_layer == IP and pkt_recv[ip_layer.name].proto != 61:
        raise RuntimeError(
            'Received packet has invalid IP protocol: {rec_proto} '
            'should be: 61'.format(rec_proto=pkt_recv[ip_layer.name].proto))


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
def main():
    """Send and receive IPsec packet."""

    args = TrafficScriptArg(
        ['tx_src_mac', 'tx_dst_mac', 'rx_src_mac', 'rx_dst_mac', 'src_ip',
         'dst_ip','crypto_alg', 'crypto_key', 'integ_alg', 'integ_key',
         'l_spi', 'r_spi'],
        ['src_tun', 'dst_tun']
    )

    tx_txq = TxQueue(args.get_arg('tx_if'))
    tx_rxq = RxQueue(args.get_arg('tx_if'))
    rx_txq = TxQueue(args.get_arg('rx_if'))
    rx_rxq = RxQueue(args.get_arg('rx_if'))

    tx_src_mac = args.get_arg('tx_src_mac')
    tx_dst_mac = args.get_arg('tx_dst_mac')
    rx_src_mac = args.get_arg('rx_src_mac')
    rx_dst_mac = args.get_arg('rx_dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    crypto_alg = args.get_arg('crypto_alg')
    crypto_key = args.get_arg('crypto_key')
    integ_alg = args.get_arg('integ_alg')
    integ_key = args.get_arg('integ_key')
    l_spi = int(args.get_arg('l_spi'))
    r_spi = int(args.get_arg('r_spi'))
    src_tun = args.get_arg('src_tun')
    dst_tun = args.get_arg('dst_tun')

    if ip_address(unicode(src_ip)).version == 6:
        ip_layer = IPv6
    else:
        ip_layer = IP

    tunnel_out = ip_layer(src=src_tun, dst=dst_tun) if src_tun and dst_tun \
        else None
    tunnel_in = ip_layer(src=dst_tun, dst=src_tun) if src_tun and dst_tun \
        else None

    if not (src_tun and dst_tun):
        src_tun = src_ip

    sa_in = SecurityAssociation(ESP, spi=r_spi, crypt_algo=crypto_alg,
                                crypt_key=crypto_key, auth_algo=integ_alg,
                                auth_key=integ_key, tunnel_header=tunnel_in)

    sa_out = SecurityAssociation(ESP, spi=l_spi, crypt_algo=crypto_alg,
                                 crypt_key=crypto_key, auth_algo=integ_alg,
                                 auth_key=integ_key, tunnel_header=tunnel_out)

    ip_pkt = ip_layer(src=src_ip, dst=dst_ip, proto=61) if ip_layer == IP \
        else ip_layer(src=src_ip, dst=dst_ip)
    ip_pkt = ip_layer(str(ip_pkt))

    e_pkt = sa_out.encrypt(ip_pkt)
    tx_pkt_send = (Ether(src=tx_src_mac, dst=tx_dst_mac) /
                   e_pkt)

    sent_packets = list()
    sent_packets.append(tx_pkt_send)
    tx_txq.send(tx_pkt_send)

    while True:
        rx_pkt_recv = rx_rxq.recv(2)

        if rx_pkt_recv is None:
            raise RuntimeError(
                '{ip} packet Rx timeout'.format(ip=ip_layer.name))

        if rx_pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    check_ip(rx_pkt_recv, ip_layer, src_ip, dst_ip)

    rx_ip_pkt = ip_layer(src=dst_ip, dst=src_ip, proto=61) if ip_layer == IP \
        else ip_layer(src=dst_ip, dst=src_ip)
    rx_pkt_send = (Ether(src=rx_dst_mac, dst=rx_src_mac) /
                   rx_ip_pkt)

    rx_txq.send(rx_pkt_send)

    while True:
        tx_pkt_recv = tx_rxq.recv(2, sent_packets)

        if tx_pkt_recv is None:
            raise RuntimeError('ESP packet Rx timeout')

        if rx_pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    check_ipsec(tx_pkt_recv, ip_layer, src_tun, dst_ip, src_ip, sa_in)

    sys.exit(0)


if __name__ == "__main__":
    main()
