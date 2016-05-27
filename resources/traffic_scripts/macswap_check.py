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

from scapy.all import Ether, IP
from resources.libraries.python.PacketVerifier import Interface
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg



def check_macswap(pkt_send, pkt_recv):
    print "Comparing following packets:"
    pkt_send.show2()
    pkt_recv.show2()

    if pkt_send.dst != pkt_recv.dst and pkt_send.src != pkt_recv.src:
        raise RuntimeError("Sent packet doesn't match received packet")


def main():
    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip'])

    src_if_name = args.get_arg('tx_if')
    dst_if_name = args.get_arg('rx_if')

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')

    src_if = Interface(src_if_name)
    dst_if = Interface(dst_if_name)

    pkt_req_send = (Ether(src=src_mac, dst=dst_mac) /
                    IP(src=src_ip, dst=dst_ip, proto=61))
    src_if.send_pkt(pkt_req_send)

    pkt_resp_recv = dst_if.recv_pkt()
    if pkt_resp_recv is None:
        raise RuntimeError('Timeout waiting for packet')

    check_macswap(pkt_req_send, pkt_resp_recv)

if __name__ == "__main__":
    main()
