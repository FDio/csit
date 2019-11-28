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

from scapy.layers.l2 import Ether, IP, ICMP
from resources.libraries.python.PacketVerifier \
    import Interface, create_gratuitous_arp_request, auto_pad, checksum_equal
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def check_ttl(ttl_begin, ttl_end, ttl_diff):
    if ttl_begin != ttl_end + ttl_diff:
        raise RuntimeError(
            f'TTL changed from {ttl_begin} to {ttl_end} but u' 
            f'decrease by {ttl_diff} expected')


def ckeck_packets_equal(pkt_send, pkt_recv):
    pkt_send_raw = auto_pad(pkt_send)
    pkt_recv_raw = auto_pad(pkt_recv)
    if pkt_send_raw != pkt_recv_raw:
        print (f"Sent:     {pkt_send_raw.encode(u'hex')}")
        print (f"Received: {pkt_recv_raw.encode(u'hex')}")
        print (f"Sent:")
        pkt_send.show2()
        print (f"Received:")
        pkt_recv.show2()
        raise RuntimeError(u"Sent packet doesn't match received packet")


def main():
    args = TrafficScriptArg([u'src_mac', u'dst_mac', u'src_ip', u'dst_ip',
                             u'hops', u'first_hop_mac', u'is_dst_tg'])

    src_if_name = args.get_arg(u'tx_if')
    dst_if_name = args.get_arg(u'rx_if')
    is_dst_tg = True if args.get_arg(u'is_dst_tg') == u'True' else False

    src_mac = args.get_arg(u'src_mac')
    first_hop_mac = args.get_arg(u'first_hop_mac')
    dst_mac = args.get_arg(u'dst_mac')
    src_ip = args.get_arg(u'src_ip')
    dst_ip = args.get_arg(u'dst_ip')
    hops = int(args.get_arg(u'hops'))

    if is_dst_tg and (src_if_name == dst_if_name):
        raise RuntimeError(
            u"Source interface name equals destination interface name")

    src_if = Interface(src_if_name)
    src_if.send_pkt(str(create_gratuitous_arp_request(src_mac, src_ip)))
    if is_dst_tg:
        dst_if = Interface(dst_if_name)
        dst_if.send_pkt(str(create_gratuitous_arp_request(dst_mac, dst_ip)))

    pkt_req_send = (Ether(src=src_mac, dst=first_hop_mac) /
                    IP(src=src_ip, dst=dst_ip) /
                    ICMP())
    src_if.send_pkt(pkt_req_send)

    if is_dst_tg:
        pkt_req_recv = dst_if.recv_pkt()
        if pkt_req_recv is None:
            raise RuntimeError(u'Timeout waiting for packet')

        check_ttl(pkt_req_send[IP].ttl, pkt_req_recv[IP].ttl, hops)
        pkt_req_send_mod = pkt_req_send.copy()
        pkt_req_send_mod[IP].ttl = pkt_req_recv[IP].ttl
        del pkt_req_send_mod[IP].chksum  # update checksum
        ckeck_packets_equal(pkt_req_send_mod[IP], pkt_req_recv[IP])

        pkt_resp_send = (Ether(src=dst_mac, dst=pkt_req_recv.src) /
                         IP(src=dst_ip, dst=src_ip) /
                         ICMP(type=0))  # echo-reply
        dst_if.send_pkt(pkt_resp_send)

    pkt_resp_recv = src_if.recv_pkt()
    if pkt_resp_recv is None:
        raise RuntimeError(u'Timeout waiting for packet')

    if is_dst_tg:
        check_ttl(pkt_resp_send[IP].ttl, pkt_resp_recv[IP].ttl, hops)
        pkt_resp_send_mod = pkt_resp_send.copy()
        pkt_resp_send_mod[IP].ttl = pkt_resp_recv[IP].ttl
        del pkt_resp_send_mod[IP].chksum  # update checksum
        ckeck_packets_equal(pkt_resp_send_mod[IP], pkt_resp_recv[IP])

    if not pkt_resp_recv.haslayer(IP):
        raise RuntimeError(f'Received packet does not contain IPv4 header: '
                           f'{pkt_resp_recv.__repr__()}')

    if pkt_resp_recv[IP].src != pkt_req_send[IP].dst:
        raise RuntimeError(
            f'Received IPv4 packet contains wrong src IP address, u'
            f'{pkt_resp_recv[IP].src} instead of {pkt_req_send[IP].dst}')

    if pkt_resp_recv[IP].dst != pkt_req_send[IP].src:
        raise RuntimeError(
            f'Received IPv4 packet contains wrong dst IP address, u'
            f'{pkt_resp_recv[IP].dst} instead of {pkt_req_send[IP].src}')

    # verify IPv4 checksum
    copy = pkt_resp_recv.copy()
    chksum = copy[IP].chksum
    del copy[IP].chksum
    tmp = IP(str(copy[IP]))
    if not checksum_equal(tmp.chksum, chksum):
        raise RuntimeError(f'Received IPv4 packet contains invalid checksum, u'
                           f'{chksum} instead of {tmp.chksum}')

    if not pkt_resp_recv[IP].haslayer(ICMP):
        raise RuntimeError(
            f'Received IPv4 packet does not contain ICMP header: '
            f'{pkt_resp_recv[IP].__repr__()}')

    # verify ICMP checksum
    copy = pkt_resp_recv.copy()
    chksum = copy[IP][ICMP].chksum
    del copy[IP][ICMP].chksum
    tmp = ICMP(str(copy[IP][ICMP]))
    if not checksum_equal(tmp.chksum, chksum):
        raise RuntimeError(f'Received ICMP packet contains invalid checksum, u'
                           f'{chksum} instead of {tmp.chksum}')

    pkt_req_send_mod = pkt_req_send.copy()
    pkt_req_send_mod[IP][ICMP].type = pkt_resp_recv[IP][ICMP].type
    del pkt_req_send_mod[IP][ICMP].chksum  # update checksum
    ckeck_packets_equal(pkt_req_send_mod[IP][ICMP], pkt_resp_recv[IP][ICMP])


if __name__ == "__main__":
    main()
