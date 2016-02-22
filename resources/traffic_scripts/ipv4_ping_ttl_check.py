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
    import Interface, create_gratuitous_arp_request, auto_pad
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def check_ttl(ttl_begin, ttl_end, ttl_diff):
    if ttl_begin != ttl_end + ttl_diff:
        raise Exception(
            "TTL changed from {} to {} but decrease by {} expected"
            .format(ttl_begin, ttl_end, ttl_diff))


def ckeck_packets_equal(pkt_send, pkt_recv):
    pkt_send_raw = auto_pad(pkt_send)
    pkt_recv_raw = auto_pad(pkt_recv)
    if pkt_send_raw != pkt_recv_raw:
        print "Sent:     {}".format(pkt_send_raw.encode('hex'))
        print "Received: {}".format(pkt_recv_raw.encode('hex'))
        print "Sent:"
        Ether(pkt_send_raw).show2()
        print "Received:"
        Ether(pkt_recv_raw).show2()
        raise Exception("Sent packet doesn't match received packet")


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
        raise Exception("Source interface name equals destination interface name")

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
            raise Exception('Timeout waiting for packet')

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
        raise Exception('Timeout waiting for packet')

    if is_dst_tg:
        check_ttl(pkt_resp_send[IP].ttl, pkt_resp_recv[IP].ttl, hops)
        pkt_resp_send_mod = pkt_resp_send.copy()
        pkt_resp_send_mod[IP].ttl = pkt_resp_recv[IP].ttl
        del pkt_resp_send_mod[IP].chksum  # update checksum
        ckeck_packets_equal(pkt_resp_send_mod[IP], pkt_resp_recv[IP])


if __name__ == "__main__":
    main()
