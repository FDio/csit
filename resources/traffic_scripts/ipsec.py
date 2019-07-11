#!/usr/bin/env python

# Copyright (c) 2019 Cisco and/or its affiliates.
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


def check_ipv4(pkt_recv, dst_tun, src_ip, dst_ip, sa_in):
    """Check received IPv4 IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param dst_tun: IPsec tunnel destination address.
    :param src_ip: Source address of original IPv4 packet.
    :param dst_ip: Destination address of original IPv4 packet.
    :param sa_in: IPsec SA for packet decryption.
    :type pkt_recv: scapy.Ether
    :type dst_tun: str
    :type src_ip: str
    :type dst_ip: str
    :type sa_in: scapy.layers.ipsec.SecurityAssociation
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(IP):
        raise RuntimeError(
            'Not an IPv4 packet received: {0}'.format(pkt_recv.__repr__()))

    if pkt_recv['IP'].dst != dst_tun:
        raise RuntimeError(
            'Received packet has invalid destination address: {0} '
            'should be: {1}'.format(pkt_recv['IP'].dst, dst_tun))

    if not pkt_recv.haslayer(ESP):
        raise RuntimeError(
            'Not an ESP packet received: {0}'.format(pkt_recv.__repr__()))

    ip_pkt = pkt_recv[IP]
    d_pkt = sa_in.decrypt(ip_pkt)

    if d_pkt[IP].dst != dst_ip:
        raise RuntimeError(
            'Decrypted packet has invalid destination address: {0} '
            'should be: {1}'.format(d_pkt['IP'].dst, dst_ip))

    if d_pkt[IP].src != src_ip:
        raise RuntimeError(
            'Decrypted packet has invalid source address: {0} should be: {1}'
            .format(d_pkt['IP'].src, src_ip))

    if not d_pkt.haslayer(ICMP):
        raise RuntimeError(
            'Decrypted packet does not have ICMP layer: {0}'.format(
                d_pkt.__repr__()))


def check_ipv6(pkt_recv, dst_tun, src_ip, dst_ip, sa_in):
    """Check received IPv6 IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param dst_tun: IPsec tunnel destination address.
    :param src_ip: Source address of original IPv6 packet.
    :param dst_ip: Destination address of original IPv6 packet.
    :param sa_in: IPsec SA for packet decryption.
    :type pkt_recv: scapy.Ether
    :type dst_tun: str
    :type src_ip: str
    :type dst_ip: str
    :type sa_in: scapy.layers.ipsec.SecurityAssociation
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(IPv6):
        raise RuntimeError(
            'Not an IPv6 packet received: {0}'.format(pkt_recv.__repr__()))

    if pkt_recv[IPv6].dst != dst_tun:
        raise RuntimeError(
            'Received packet has invalid destination address: {0} '
            'should be: {1}'.format(pkt_recv['IPv6'].dst, dst_tun))

    if not pkt_recv.haslayer(ESP):
        raise RuntimeError(
            'Not an ESP packet received: {0}'.format(pkt_recv.__repr__()))

    ip_pkt = pkt_recv[IPv6]
    d_pkt = sa_in.decrypt(ip_pkt)

    if d_pkt[IPv6].dst != dst_ip:
        raise RuntimeError(
            'Decrypted packet has invalid destination address {0}: '
            'should be: {1}'.format(d_pkt['IPv6'].dst, dst_ip))

    if d_pkt[IPv6].src != src_ip:
        raise RuntimeError(
            'Decrypted packet has invalid source address: {0} should be: {1}'
            .format(d_pkt['IPv6'].src, src_ip))

    if not d_pkt.haslayer(ICMPv6EchoReply):
        raise RuntimeError(
            'Decrypted packet does not have ICMP layer: {0}'.format(
                d_pkt.__repr__()))


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
def main():
    """Send and receive IPsec packet."""
    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip',
                             'crypto_alg', 'crypto_key','l_spi', 'r_spi'],
                            ['integ_alg', 'integ_key', 'src_tun', 'dst_tun'])

    rxq = RxQueue(args.get_arg('rx_if'))
    txq = TxQueue(args.get_arg('tx_if'))

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
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

    is_ipv4 = True
    if 6 == ip_address(unicode(src_ip)).version:
        is_ipv4 = False

    tunnel_out = None
    tunnel_in = None

    if src_tun and dst_tun:
        if is_ipv4:
            tunnel_out = IP(src=src_tun, dst=dst_tun)
            tunnel_in = IP(src=dst_tun, dst=src_tun)
        else:
            tunnel_out = IPv6(src=src_tun, dst=dst_tun)
            tunnel_in = IPv6(src=dst_tun, dst=src_tun)
    else:
        src_tun = src_ip
        dst_tun = dst_ip

    # Scapy is considering key and salt to be part of crypt_key string:
    # https://github.com/secdev/scapy/blob/master/scapy/layers/ipsec.py#L816
    # For this reason key_len != len(crypto_key) for selected crypto algorithms.
    if crypto_alg == 'AES-CTR' or crypto_alg == 'AES-GCM':
        crypto_key = crypto_key + 'salt'
    if crypto_alg == 'AES-CCM':
        crypto_key = crypto_key + 'slt'

    sa_in = SecurityAssociation(ESP, spi=r_spi, crypt_algo=crypto_alg,
                                crypt_key=crypto_key, auth_algo=integ_alg,
                                auth_key=integ_key, tunnel_header=tunnel_in)

    sa_out = SecurityAssociation(ESP, spi=l_spi, crypt_algo=crypto_alg,
                                 crypt_key=crypto_key, auth_algo=integ_alg,
                                 auth_key=integ_key, tunnel_header=tunnel_out)

    sent_packets = []

    if is_ipv4:
        ip_pkt = (IP(src=src_ip, dst=dst_ip) /
                  ICMP())
        ip_pkt = IP(str(ip_pkt))
    else:
        ip_pkt = (IPv6(src=src_ip, dst=dst_ip) /
                  ICMPv6EchoRequest())
        ip_pkt = IPv6(str(ip_pkt))

    e_pkt = sa_out.encrypt(ip_pkt)
    pkt_send = (Ether(src=src_mac, dst=dst_mac) /
                e_pkt)

    sent_packets.append(pkt_send)
    txq.send(pkt_send)

    while True:
        pkt_recv = rxq.recv(2, sent_packets)

        if pkt_recv is None:
            raise RuntimeError('ESP packet Rx timeout')

        if pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if is_ipv4:
        check_ipv4(pkt_recv, src_tun, dst_ip, src_ip, sa_in)
    else:
        check_ipv6(pkt_recv, src_tun, dst_ip, src_ip, sa_in)

    sys.exit(0)


if __name__ == "__main__":
    main()
