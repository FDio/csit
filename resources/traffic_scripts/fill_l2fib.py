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

"""Traffic script that sends an ip icmp packet(s) from changing MAC source addresses to fill up the
l2fib table entries on Bridge domain"""

import sys
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from scapy.layers.inet import ICMP, IP
from scapy.all import Ether
from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal
from robot.api import logger


import random
#
def randomized_MAC():
    mac = [ random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff),
	    random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))

def create_random_MAC_list(count):
    index = 0
    identical = 0
    mac_adr = {}
    if count <= 0:
       raise RuntimeError('Invalid count of packets to send')
    while index < count:
      mac_fin = randomized_MAC()
      if mac_adr.has_key(mac_fin) != True:
         mac_adr[mac_fin] = index
         index = index + 1
      else:
	identical = identical + 1
    logger.debug('Identical MACs {0}'.format(identical))
    logger.debug('indexxxx: {0}'.format(index))
    return mac_adr

def main():
    """ Send IP icmp packet from one traffic generator interface to the other"""

    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip', 'pkt_count'])

    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    pkt_count = int(args.get_arg('pkt_count'))
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    MAC_list = create_random_MAC_list(pkt_count)
    logger.debug('Mac_list size: {0}'.format(len(MAC_list)))
    for src_mac in MAC_list:
      #src_mac = randomizedMAC()
      # Create empty ip ICMP packet and add padding before sending
      pkt_raw = Ether(src=src_mac, dst=dst_mac) / \
	IP(src=src_ip, dst=dst_ip) / \
        ICMP()

      # Send created packet on one interface and receive on the other
      txq.send(pkt_raw)

      ether = rxq.recv(10)

      # Check whether received packet contains layers Ether, IP and ICMP
      if ether is None:
        raise RuntimeError('ICMP echo Rx timeout')

      if not ether.haslayer(IP):
        raise RuntimeError(
            'Not an IP packet received {0}'.format(ether.__repr__()))

      if not ether.haslayer(ICMP):
        raise RuntimeError(
            'Not an ICMP packet received {0}'.format(ether.__repr__()))

    sys.exit(0)

if __name__ == "__main__":
    main()
