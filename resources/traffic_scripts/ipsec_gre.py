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

from scapy.all import Ether, IP, ICMP
from scapy.layers.ipsec import SecurityAssociation, ESP

from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue


def check_ipv4(pkt_recv, sa_in, params):
    """Check received IPv4 IPSec packet for correct encapsulation
    and GRE header.

    In params, one should expect to find these (all are mandatory):
        gre_src_ip  - Source IP address in GRE/IPSec header.
        gre_dst_ip  - Destination IP address in GRE/IPSec header.
        gre_src_mac - Source MAC address in GRE/IPSec header.
        gre_dst_mac - Destination MAC address in GRE/IPSec header.
        src_ip - Source IP address of a original packet.
        dst_ip - Destination IP address of a original packet.

    :param pkt_recv: Received packet to verify.
    :param sa_in: IPsec SA for packet decryption.
    :param params: Dictionary of additional parameters.
    :type pkt_recv: scapy.Ether
    :type sa_in: scapy.layers.ipsec.SecurityAssociation
    :type params: dict
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(IP):
        raise RuntimeError(
            'Not an IPv4 packet received: {0}'.format(pkt_recv.__repr__()))

    if pkt_recv['IP'].dst != params['gre_dst_ip']:
        raise RuntimeError(
            'Received packet has invalid destination address: {0} '
            'should be: {1}'.format(pkt_recv['IP'].dst, params['gre_dst_ip']))

    if not pkt_recv.haslayer(ESP):
        raise RuntimeError(
            'Not an ESP packet received: {0}'.format(pkt_recv.__repr__()))

    ip_pkt = pkt_recv['IP']
    d_pkt = sa_in.decrypt(ip_pkt)
    if d_pkt['IP'].dst != params['gre_dst_ip']:
        raise RuntimeError(
            'Decrypted packet has invalid destination address: {0} '
            'should be: {1}'.format(d_pkt['IP'].dst, params['gre_dst_ip']))

    if d_pkt['IP'].src != params['gre_src_ip']:
        raise RuntimeError(
            'Decrypted packet has invalid source address: {0} should be: {1}'
            .format(d_pkt['IP'].src, params['gre_src_ip']))

    if not d_pkt.haslayer('GRE'):
        raise RuntimeError(
            'Decrypted packet does not have GRE layer:l {0}'.format(
                d_pkt.__repr__()))

    if d_pkt['GRE']['IP'].src != params['src_ip']:
        raise RuntimeError(
            'Decrypted packet does not contain source IP address: {0} '
            'should be {1}'.format(params['src_ip'])
        )
    if d_pkt['GRE']['IP'].dst != params['dst_ip']:
        raise RuntimeError(
            'Decrypted packet does not contain destination IP address: {0} '
            'should be {1}'.format(params['dst_ip'])
        )


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
def main():
    """Send and receive IPSec packet."""

    args = TrafficScriptArg(['src_ip', 'dst_ip', 'src_gre_ip', 'dst_gre_ip',
                             'src_mac', 'dst_mac', 'src_gre_mac', 'dst_gre_mac',
                             'crypto_alg', 'crypto_key', 'integ_alg',
                             'integ_key', 'spi'])

    rxq = RxQueue(args.get_arg('rx_if'))
    txq = TxQueue(args.get_arg('tx_if'))

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    gre_src_mac = args.get_arg('src_gre_mac')
    gre_dst_mac = args.get_arg('dst_gre_mac')
    gre_src_ip = args.get_arg('src_gre_ip')
    gre_dst_ip = args.get_arg('dst_gre_ip')
    crypto_alg = args.get_arg('crypto_alg')
    crypto_key = args.get_arg('crypto_key')
    integ_alg = args.get_arg('integ_alg')
    integ_key = args.get_arg('integ_key')
    spi = int(args.get_arg('spi'))

    sa_in = SecurityAssociation(ESP, spi=spi, crypt_algo=crypto_alg,
                                crypt_key=crypto_key, auth_algo=integ_alg,
                                auth_key=integ_key)

    pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
               IP(src=src_ip, dst=dst_ip) /
               ICMP())

    sent_packets = [pkt_raw]

    txq.send(pkt_raw)

    pkt_recv = rxq.recv(2, sent_packets)

    if pkt_recv is None:
        raise RuntimeError('ESP packet Rx timeout')

    params = {
        'gre_src_ip': gre_src_ip,
        'gre_dst_ip': gre_dst_ip,
        'gre_src_mac': gre_src_mac,
        'gre_dst_mac': gre_dst_mac,
        'src_ip': src_ip,
        'dst_ip': dst_ip
    }
    check_ipv4(pkt_recv, sa_in, params)

    sys.exit(0)


if __name__ == "__main__":
    main()
