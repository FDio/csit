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
from optparse import OptionParser


def check_ttl(ttl_begin, ttl_end, ttl_diff):
    if ttl_begin != ttl_end + ttl_diff:
        src_if.close()
        if dst_if_defined:
            dst_if.close()
        raise Exception(
            "TTL changed from {} to {} but decrease by {} expected"
            .format(ttl_begin, ttl_end, hops))


def ckeck_packets_equal(pkt_send, pkt_recv):
    pkt_send_raw = str(pkt_send)
    pkt_recv_raw = str(pkt_recv)
    if pkt_send_raw != pkt_recv_raw:
        print "Sent:     {}".format(pkt_send_raw.encode('hex'))
        print "Received: {}".format(pkt_recv_raw.encode('hex'))
        print "Sent:"
        Ether(pkt_send_raw).show2()
        print "Received:"
        Ether(pkt_recv_raw).show2()
        src_if.close()
        if dst_if_defined:
            dst_if.close()
        raise Exception("Sent packet doesn't match received packet")


parser = OptionParser()
parser.add_option("--src_if", dest="src_if")
parser.add_option("--dst_if", dest="dst_if")  # optional
parser.add_option("--src_mac", dest="src_mac")
parser.add_option("--first_hop_mac", dest="first_hop_mac")
parser.add_option("--dst_mac", dest="dst_mac")  # optional
parser.add_option("--src_ip", dest="src_ip")
parser.add_option("--dst_ip", dest="dst_ip")
parser.add_option("--hops", dest="hops")  # optional
# If one of 'dst_if', 'dst_mac' and 'hops' is specified all must be specified.
(opts, args) = parser.parse_args()
src_if_name = opts.src_if
dst_if_name = opts.dst_if
dst_if_defined = True
if dst_if_name is None:
    dst_if_defined = False
src_mac = opts.src_mac
first_hop_mac = opts.first_hop_mac
dst_mac = opts.dst_mac
src_ip = opts.src_ip
dst_ip = opts.dst_ip
hops = int(opts.hops)

if dst_if_defined and (src_if_name == dst_if_name):
    raise Exception("Source interface name equals destination interface name")

src_if = Interface(src_if_name)
src_if.send_pkt(create_gratuitous_arp_request(src_mac, src_ip))
if dst_if_defined:
    dst_if = Interface(dst_if_name)
    dst_if.send_pkt(create_gratuitous_arp_request(dst_mac, dst_ip))

pkt_req_send = auto_pad(Ether(src=src_mac, dst=first_hop_mac) /
                        IP(src=src_ip, dst=dst_ip) /
                        ICMP())
pkt_req_send = Ether(pkt_req_send)
src_if.send_pkt(pkt_req_send)

if dst_if_defined:
    try:
        pkt_req_recv = dst_if.recv_pkt()
    except:
        src_if.close()
        if dst_if_defined:
            dst_if.close()
        raise

    check_ttl(pkt_req_send[IP].ttl, pkt_req_recv[IP].ttl, hops)
    pkt_req_send_mod = pkt_req_send.copy()
    pkt_req_send_mod[IP].ttl = pkt_req_recv[IP].ttl
    del pkt_req_send_mod[IP].chksum  # update checksum
    ckeck_packets_equal(pkt_req_send_mod[IP], pkt_req_recv[IP])

    pkt_resp_send = auto_pad(Ether(src=dst_mac, dst=pkt_req_recv.src) /
                             IP(src=dst_ip, dst=src_ip) /
                             ICMP(type=0))  # echo-reply
    pkt_resp_send = Ether(pkt_resp_send)
    dst_if.send_pkt(pkt_resp_send)

try:
    pkt_resp_recv = src_if.recv_pkt()
except:
    src_if.close()
    if dst_if_defined:
        dst_if.close()
    raise

if dst_if_defined:
    check_ttl(pkt_resp_send[IP].ttl, pkt_resp_recv[IP].ttl, hops)
    pkt_resp_send_mod = pkt_resp_send.copy()
    pkt_resp_send_mod[IP].ttl = pkt_resp_recv[IP].ttl
    del pkt_resp_send_mod[IP].chksum  # update checksum
    ckeck_packets_equal(pkt_resp_send_mod[IP], pkt_resp_recv[IP])

src_if.close()
if dst_if_defined:
    dst_if.close()
