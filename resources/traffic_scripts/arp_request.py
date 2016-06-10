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

"""Send an ARP request and verify the reply"""

import sys

from scapy.all import Ether, ARP

from resources.libraries.python.PacketVerifier import Interface
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def parse_arguments():
    """Parse arguments of the script passed through command line

    :return: tuple of parsed arguments
    """
    args = TrafficScriptArg(['src_if', 'src_mac', 'dst_mac',
                             'src_ip', 'dst_ip'])

    # check for mandatory parameters
    params = (args.get_arg('tx_if'),
              args.get_arg('src_mac'),
              args.get_arg('dst_mac'),
              args.get_arg('src_ip'),
              args.get_arg('dst_ip'))
    if None in params:
        raise Exception('Missing mandatory parameter(s)!')

    return params


def arp_request_test():
    """Send ARP request, expect a reply and verify its fields.

    returns: test status
    :raises RuntimeError: ARP reply timeout.
    """
    test_passed = False
    (src_if, src_mac, dst_mac, src_ip, dst_ip) = parse_arguments()

    interface = Interface(src_if)

    # build an ARP request
    arp_request = (Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff') /
                   ARP(psrc=src_ip, hwsrc=src_mac, pdst=dst_ip,
                       hwdst='ff:ff:ff:ff:ff:ff'))

    # send the request
    interface.send_pkt(arp_request)

    try:
        # wait for APR reply
        ether = interface.recv_pkt()

        if not ether:
            raise RuntimeError("ARP reply timeout")

        # verify received packet

        if not ether.haslayer(ARP):
            raise RuntimeError('Unexpected packet: does not contain ARP ' +
                               'header "{}"'.format(ether.__repr__()))

        arp = ether['ARP']
        arp_reply = 2

        if arp.op != arp_reply:
            raise RuntimeError('expected op={}, received {}'.format(arp_reply,
                                                                    arp.op))
        if arp.ptype != 0x800:
            raise RuntimeError('expected ptype=0x800, received {}'.
                               format(arp.ptype))
        if arp.hwlen != 6:
            raise RuntimeError('expected hwlen=6, received {}'.
                               format(arp.hwlen))
        if arp.plen != 4:
            raise RuntimeError('expected plen=4, received {}'.format(arp.plen))
        if arp.hwsrc != dst_mac:
            raise RuntimeError('expected hwsrc={}, received {}'.
                               format(dst_mac, arp.hwsrc))
        if arp.psrc != dst_ip:
            raise RuntimeError('expected psrc={}, received {}'.
                               format(dst_ip, arp.psrc))
        if arp.hwdst != src_mac:
            raise RuntimeError('expected hwdst={}, received {}'.
                               format(src_mac, arp.hwdst))
        if arp.pdst != src_ip:
            raise RuntimeError('expected pdst={}, received {}'.
                               format(src_ip, arp.pdst))
        test_passed = True

    except RuntimeError as ex:
        print 'Error occurred: {}'.format(ex)

    return test_passed


def main():
    """Run the test and collect result"""
    if arp_request_test():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
