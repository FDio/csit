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
from subprocess import call

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import Ether, IP, ICMP, IPv6, ICMPv6EchoRequest, ICMPv6EchoReply
from scapy.layers.ipsec import SecurityAssociation, ESP
from ipaddress import ip_address

from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue

def main():
    output = call(["sudo", "vppctl", "sh", "ikev2", "sa"])
    print output
    sa_out = SecurityAssociation(ESP, spi='9cf58ae1', crypt_algo='AES-CBC',
                                 crypt_key='9ed96e04313ecd6dffb9c87ba6740cdf11fa4e866f1e65fb', auth_algo='HMAC-SHA1-96',
                                 auth_key='f3379abd8d96f5dd53f912c24f2a88308e667233')

    sent_packets = []

    ip_pkt = IP(src='10.0.0.10', dst='10.0.0.5') / \
             ICMP()
    ip_pkt = IP(str(ip_pkt))

    e_pkt = sa_out.encrypt(ip_pkt)
    pkt_send = Ether(src='08:00:27:7e:6e:2e', dst='08:00:27:9b:f1:65') / \
               e_pkt

    sent_packets.append(pkt_send)
    txq.send(pkt_send)