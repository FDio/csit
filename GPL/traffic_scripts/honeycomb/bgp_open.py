#!/usr/bin/env python

# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.

"""Traffic script that listens for incoming BGP connections and verifies
received GBP Open message."""

import sys
import socket

from scapy.main import load_contrib
from scapy.layers.inet import Raw
from scapy.contrib.bgp import BGPHeader, BGPOpen

from ..TrafficScriptArg import TrafficScriptArg


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
