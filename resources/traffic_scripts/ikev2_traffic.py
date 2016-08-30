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

"""Traffic script that sends an IP ICMPv4/ICMPv6 packet from one interface
to the other. Source and destination IP addresses and source and destination
MAC addresses are checked in received packet.
"""

import sys
from ipaddress import ip_address
from subprocess import check_output

from scapy.layers.inet import ICMP, IP, UDP
from scapy.layers.inet6 import IPv6
from scapy.all import Ether
from scapy.layers.inet6 import ICMPv6EchoRequest, ICMPv6EchoReply
from robot.api import logger

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from scapy.layers.ipsec import SecurityAssociation, ESP


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

    ip_pkt = pkt_recv['IP']
    d_pkt = sa_in.decrypt(ip_pkt)

    print "==================="
    print d_pkt.show()
    print "==================="
    if d_pkt['IP'].dst != dst_ip:
        raise RuntimeError(
            'Decrypted packet has invalid destination address: {0} '
            'should be: {1}'.format(d_pkt['IP'].dst, dst_ip))

    if d_pkt['IP'].src != src_ip:
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

    if pkt_recv['IPv6'].dst != dst_tun:
        raise RuntimeError(
            'Received packet has invalid destination address: {0} '
            'should be: {1}'.format(pkt_recv['IPv6'].dst, dst_tun))

    if not pkt_recv.haslayer(ESP):
        raise RuntimeError(
            'Not an ESP packet received: {0}'.format(pkt_recv.__repr__()))

    ip_pkt = pkt_recv['IPv6']
    d_pkt = sa_in.decrypt(ip_pkt)

    if d_pkt['IPv6'].dst != dst_ip:
        raise RuntimeError(
            'Decrypted packet has invalid destination address {0}: '
            'should be: {1}'.format(d_pkt['IPv6'].dst, dst_ip))

    if d_pkt['IPv6'].src != src_ip:
        raise RuntimeError(
            'Decrypted packet has invalid source address: {0} should be: {1}'
            .format(d_pkt['IPv6'].src, src_ip))

    if not d_pkt.haslayer(ICMPv6EchoReply):
        raise RuntimeError(
            'Decrypted packet does not have ICMP layer: {0}'.format(
                d_pkt.__repr__()))

def main():
    """Send IP ICMP packet from one traffic generator interface to the other."""
    args = TrafficScriptArg(
        ['src_mac', 'dst_mac', 'src_ip', 'dst_ip', 'rSpi', 'rEnc', 'rAuth',
         'lSpi', 'lEnc', 'lAuth', 'src_tun_ip', 'dst_tun_ip'])

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    src_tun_ip = args.get_arg('src_tun_ip')
    dst_tun_ip = args.get_arg('dst_tun_ip')
    tx_if = args.get_arg('tx_if')
    r_Spi = args.get_arg('rSpi')
    r_Enc = args.get_arg('rEnc')
    r_Auth = args.get_arg('rAuth')
    l_Spi = args.get_arg('lSpi')
    l_Enc = args.get_arg('lEnc')
    l_Auth = args.get_arg('lAuth')

    txq = TxQueue(tx_if)
    rxq = RxQueue(tx_if)
    sent_packets = []

    is_ipv4 = True
    if 6 == ip_address(unicode(src_ip)).version:
        is_ipv4 = False

    r_Enc = r_Enc.decode('hex')
    r_Auth = r_Auth.decode('hex')
    l_Enc = l_Enc.decode('hex')
    l_Auth = l_Auth.decode('hex')
    r_Spi = int(r_Spi)
    l_Spi = int(l_Spi)

    tunnel_out = IP(src=src_tun_ip,dst=dst_tun_ip)
    tunnel_in = IP(src=dst_tun_ip,dst=src_tun_ip)
    sa_out = SecurityAssociation(ESP, spi=r_Spi, crypt_algo='AES-CBC',
                             crypt_key=r_Enc, auth_algo='HMAC-SHA1-96',
                             auth_key=r_Auth, tunnel_header=tunnel_out)

    sa_in = SecurityAssociation(ESP, spi=l_Spi, crypt_algo='AES-CBC',
                                 crypt_key=l_Enc, auth_algo='HMAC-SHA1-96',
                                 auth_key=l_Auth, tunnel_header=tunnel_in)

    ip_pkt = IP(src=src_ip, dst=dst_ip) / \
             ICMP()
    ip_pkt = IP(str(ip_pkt))


    e_pkt = sa_out.encrypt(ip_pkt)
    pkt_send = Ether(src=src_mac, dst=dst_mac) / \
               e_pkt

    sent_packets.append(pkt_send)
    txq.send(pkt_send)

    pkt_recv = rxq.recv(2, sent_packets)

    if pkt_recv is None:
        raise RuntimeError('Rx timeout')

    if is_ipv4:
        check_ipv4(pkt_recv, src_tun_ip, dst_ip, src_ip, sa_in)
    else:
        print "IPv6 not supported"
        # check_ipv6(pkt_recv, sa_in, dst_ip, src_ip, sa_in)

    sys.exit(0)


if __name__ == "__main__":
    main()
