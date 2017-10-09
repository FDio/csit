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

"""Traffic script that listens for incoming BGP connections and verifies
received GBP Open message."""

import sys
import socket

from scapy.main import load_contrib
from scapy.layers.inet import Raw
from scapy.contrib.bgp import BGPHeader, BGPOpen

from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def main():
    """Open a TCP listener socket on the default BGP port. Accept an incoming
    connection, receive data and verify if data is a valid BGP Open message."""
    args = TrafficScriptArg(['rx_ip', 'src_ip', 'rx_port', 'as_number',
                             'holdtime'])

    rx_ip = args.get_arg('rx_ip')
    src_ip = args.get_arg('src_ip')
    rx_port = int(args.get_arg('rx_port'))
    as_number = int(args.get_arg('as_number'))
    holdtime = int(args.get_arg('holdtime'))

    load_contrib("bgp")

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind((rx_ip, rx_port))
    soc.listen(1)

    print "Listener active, awaiting connection..."
    soc.settimeout(8)
    conn, addr = soc.accept()
    print 'Connection established with peer:', addr

    data = conn.recv(256)
    conn.close()
    soc.close()

    bgp_layer = (BGPHeader(Raw(data).load))
    bgp_layer.show()

    if not bgp_layer.haslayer(BGPOpen):
        raise RuntimeError("Received data is not a BGP OPEN message.")
    bgp_open = bgp_layer.getlayer(BGPOpen)
    if bgp_open.bgp_id != src_ip:
        raise RuntimeError(
            "BGP ID mismatch. Received {0} but should be {1}".
            format(bgp_open.bgp_id, src_ip))
    else:
        print "BGP ID matched."

    if bgp_open.AS != as_number:
        raise RuntimeError(
            "BGP AS number mismatch. Received {0} but should be {1}".
            format(bgp_open.AS, as_number))
    else:
        print "BGP AS number matched."

    if bgp_open.hold_time != holdtime:
        raise RuntimeError(
            "Hold Time parameter mismatch. Received {0} but should be {1}.".
            format(bgp_layer.getlayer(BGPOpen).holdtime, holdtime))
    else:
        print "BGP Hold Time parameter matched."

    sys.exit(0)

if __name__ == "__main__":
    main()
