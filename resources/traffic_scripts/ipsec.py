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

"""Traffic script for IPsec verification."""

import sys
import logging

# pylint: disable=no-name-in-module
# pylint: disable=import-error
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.all import Ether
from scapy.layers.inet import ICMP, IP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.layers.inet6 import ICMPv6EchoRequest, ICMPv6EchoReply
from scapy.layers.ipsec import SecurityAssociation, ESP
from ipaddress import ip_address

from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue


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

    icmp_layer = ICMPv6EchoReply if ip_layer == IPv6 else ICMP

    if not d_pkt.haslayer(icmp_layer):
        raise RuntimeError(
            'Decrypted packet does not have {icmp} layer: {pkt}'.format(
                icmp=icmp_layer.name, pkt=d_pkt.__repr__()))


def check_icmp(pkt_recv, ip_layer, src_ip, dst_ip):
    """Check received IPv6 IPsec packet.

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

    icmp_layer = ICMPv6EchoRequest if ip_layer == IPv6 else ICMP

    if not pkt_recv.haslayer(icmp_layer):
        raise RuntimeError(
            'Received packet does not have {icmp} layer: {pkt}'.format(
                icmp=icmp_layer.name, pkt=pkt_recv.__repr__()))


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
        icmp_reqest = ICMPv6EchoRequest
        icmp_reply = ICMPv6EchoReply
    else:
        ip_layer = IP
        icmp_reqest = ICMP
        icmp_reply = ICMP

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

    ip_pkt = (ip_layer(src=src_ip, dst=dst_ip) /
              icmp_reqest())
    ip_pkt = IP(str(ip_pkt))

    e_pkt = sa_out.encrypt(ip_pkt)
    tx_pkt_send = (Ether(src=tx_src_mac, dst=tx_dst_mac) /
                   e_pkt)

    sent_packets = list()
    sent_packets.append(tx_pkt_send)
    tx_txq.send(tx_pkt_send)

    while True:
        rx_pkt_recv = rx_rxq.recv(2, sent_packets)

        if rx_pkt_recv is None:
            raise RuntimeError('ICMP/ICMPv6 echo request Rx timeout')

        if rx_pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    check_icmp(rx_pkt_recv, ip_layer, src_ip, dst_ip)

    rx_pkt_send = (Ether(src=rx_dst_mac, dst=rx_src_mac) /
                   ip_layer(src=dst_ip, dst=src_ip) /
                   icmp_reply())

    del sent_packets[:]
    sent_packets.append(rx_pkt_send)
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

    check_ipsec(rx_pkt_recv, ip_layer, src_tun, dst_ip, src_ip, sa_in)

    sys.exit(0)


if __name__ == "__main__":
    main()
