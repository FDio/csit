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

from scapy.all import Ether, IP, ICMP
from resources.libraries.python.PacketVerifier \
    import Interface, create_gratuitous_arp_request, auto_pad, checksum_equal
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def check_ttl(ttl_begin, ttl_end, ttl_diff):
    if ttl_begin != ttl_end + ttl_diff:
        raise RuntimeError(
            "TTL changed from {} to {} but decrease by {} expected"
            .format(ttl_begin, ttl_end, ttl_diff))


def ckeck_packets_equal(pkt_send, pkt_recv):
    pkt_send_raw = auto_pad(pkt_send)
    pkt_recv_raw = auto_pad(pkt_recv)
    if pkt_send_raw != pkt_recv_raw:
        print "Sent:     {}".format(pkt_send_raw.encode('hex'))
        print "Received: {}".format(pkt_recv_raw.encode('hex'))
        print "Sent:"
        pkt_send.show2()
        print "Received:"
        pkt_recv.show2()
        raise RuntimeError("Sent packet doesn't match received packet")


def main():
    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip',
                             'hops', 'first_hop_mac', 'is_dst_tg'])

    src_if_name = args.get_arg('tx_if')
    dst_if_name = args.get_arg('rx_if')
    is_dst_tg = True if args.get_arg('is_dst_tg') == 'True' else False

    src_mac = args.get_arg('src_mac')
    first_hop_mac = args.get_arg('first_hop_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    hops = int(args.get_arg('hops'))

    if is_dst_tg and (src_if_name == dst_if_name):
        raise RuntimeError(
            "Source interface name equals destination interface name")

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
            raise RuntimeError('Timeout waiting for packet')

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
        raise RuntimeError('Timeout waiting for packet')

    if is_dst_tg:
        check_ttl(pkt_resp_send[IP].ttl, pkt_resp_recv[IP].ttl, hops)
        pkt_resp_send_mod = pkt_resp_send.copy()
        pkt_resp_send_mod[IP].ttl = pkt_resp_recv[IP].ttl
        del pkt_resp_send_mod[IP].chksum  # update checksum
        ckeck_packets_equal(pkt_resp_send_mod[IP], pkt_resp_recv[IP])

    if not pkt_resp_recv.haslayer(IP):
        raise RuntimeError('Received packet does not contain IPv4 header: {}'.
                           format(pkt_resp_recv.__repr__()))

    if pkt_resp_recv[IP].src != pkt_req_send[IP].dst:
        raise RuntimeError(
            'Received IPv4 packet contains wrong src IP address, '
            '{} instead of {}'.format(pkt_resp_recv[IP].src,
                                      pkt_req_send[IP].dst))

    if pkt_resp_recv[IP].dst != pkt_req_send[IP].src:
        raise RuntimeError(
            'Received IPv4 packet contains wrong dst IP address, '
            '{} instead of {}'.format(pkt_resp_recv[IP].dst,
                                      pkt_req_send[IP].src))

    # verify IPv4 checksum
    copy = pkt_resp_recv.copy()
    chksum = copy[IP].chksum
    del copy[IP].chksum
    tmp = IP(str(copy[IP]))
    if not checksum_equal(tmp.chksum, chksum):
        raise RuntimeError('Received IPv4 packet contains invalid checksum, '
                           '{} instead of {}'.format(chksum, tmp.chksum))

    if not pkt_resp_recv[IP].haslayer(ICMP):
        raise RuntimeError(
            'Received IPv4 packet does not contain ICMP header: {}'.
            format(pkt_resp_recv[IP].__repr__()))

    # verify ICMP checksum
    copy = pkt_resp_recv.copy()
    chksum = copy[IP][ICMP].chksum
    del copy[IP][ICMP].chksum
    tmp = ICMP(str(copy[IP][ICMP]))
    if not checksum_equal(tmp.chksum, chksum):
        raise RuntimeError('Received ICMP packet contains invalid checksum, '
                           '{} instead of {}'.format(chksum, tmp.chksum))

    pkt_req_send_mod = pkt_req_send.copy()
    pkt_req_send_mod[IP][ICMP].type = pkt_resp_recv[IP][ICMP].type
    del pkt_req_send_mod[IP][ICMP].chksum  # update checksum
    ckeck_packets_equal(pkt_req_send_mod[IP][ICMP], pkt_resp_recv[IP][ICMP])


if __name__ == "__main__":
    main()
