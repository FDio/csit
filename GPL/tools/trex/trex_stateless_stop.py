#!/usr/bin/python3

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

"""This script uses T-REX stateless API to drive t-rex instance.

Requirements:
- T-REX: https://github.com/cisco-system-traffic-generator/trex-core
 - compiled and running T-REX process (eg. ./t-rex-64 -i)
 - trex.stl.api library
- Script must be executed on a node with T-REX instance

Functionality:
1. Stop any running traffic
2. Optionally restore reference counter values.
3. Return conter differences.
"""

import argparse
import json
import sys

from collections import OrderedDict  # Needed to parse xstats representation.

sys.path.insert(
    0, u"/opt/trex-core-2.61/scripts/automation/trex_control_plane/interactive/"
)
from trex.stl.api import *


def main():
    """Stop traffic if any is running. Report xstats."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        u"--xstat0", type=str, default=u"",
        help=u"Reference xstat object if any."
    )
    parser.add_argument(
        u"--xstat1", type=str, default=u"",
        help=u"Reference xstat object if any."
    )
    args = parser.parse_args()

    client = STLClient()
    try:
        # connect to server
        client.connect()

        client.acquire(force=True)
        # TODO: Support unidirection.
        client.stop(ports=[0, 1])

        # Read the stats after the test,
        # we need to update values before the last trial started.
        if args.xstat0:
            snapshot = eval(args.xstat0)
            client.ports[0].get_xstats().reference_stats = snapshot
        if args.xstat1:
            snapshot = eval(args.xstat1)
            client.ports[1].get_xstats().reference_stats = snapshot
        # Now we can call the official method to get differences.
        xstats0 = client.get_xstats(0)
        xstats1 = client.get_xstats(1)

    # If STLError happens, let the script fail with stack trace.
    finally:
        client.disconnect()

    print(u"##### statistics port 0 #####")
    print(json.dumps(xstats0, indent=4, separators=(u",", u": ")))
    print(u"##### statistics port 1 #####")
    print(json.dumps(xstats1, indent=4, separators=(u",", u": ")))

    tx_0, rx_0 = xstats0[u"tx_good_packets"], xstats0[u"rx_good_packets"]
    tx_1, rx_1 = xstats1[u"tx_good_packets"], xstats1[u"rx_good_packets"]
    lost_a, lost_b = tx_0 - rx_1, tx_1 - rx_0

    print(f"\npackets lost from 0 --> 1:   {lost_a} pkts")
    print(f"packets lost from 1 --> 0:   {lost_b} pkts")

    total_rcvd, total_sent = rx_0 + rx_1, tx_0 + tx_1
    total_lost = total_sent - total_rcvd
    # TODO: Add latency.
    print(
        f"rate='unknown', totalReceived={total_rcvd}, totalSent={total_sent}, "
        f"frameLoss={total_lost}, latencyStream0(usec)=-1/-1/-1, "
        f"latencyStream1(usec)=-1/-1/-1, targetDuration='manual'"
    )


if __name__ == u"__main__":
    main()
