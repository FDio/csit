#!/usr/bin/python3

# Copyright (c) 2022 Cisco and/or its affiliates.
#
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
#
# Licensed under the Apache License 2.0 or
# GNU General Public License v2.0 or later;  you may not use this file
# except in compliance with one of these Licenses. You
# may obtain a copy of the Licenses at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
#
# Note: If this file is linked with Scapy, which is GPLv2+, your use of it
# must be under GPLv2+.  If at any point in the future it is no longer linked
# with Scapy (or other GPLv2+ licensed software), you are free to choose
# Apache 2.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script uses T-REX advanced stateful API to drive t-rex instance.

Requirements:
- T-REX: https://github.com/cisco-system-traffic-generator/trex-core
 - compiled and running T-REX process (eg. ./t-rex-64 -i)
 - trex.astf.api library
- Script must be executed on a node with T-REX instance

Functionality:
1. Stop any running traffic
2. Optionally restore reference counter values.
3. Return conter differences.
"""

import argparse
import json
import sys
import time

sys.path.insert(
    0, u"/opt/trex-core-2.97/scripts/automation/trex_control_plane/interactive/"
)
from trex.astf.api import ASTFClient, ASTFProfile, TRexError

from collections import OrderedDict  # Needed to parse xstats representation.


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

    print(u"DEBUG args parsed")
    client = ASTFClient()
    print(u"DEBUG client created")
    try:
        # connect to server
        client.connect()
        print(u"DEBUG client connected")

        client.acquire(force=True)
        print(u"DEBUG ports acquired")
        client.stop()
        print(u"DEBUG stop called")

        # Read the stats after the test,
        # we need to update values before the last trial started.
        if args.xstat0:
            snapshot = eval(args.xstat0)
            client.ports[0].get_xstats().reference_stats = snapshot
            print(u"DEBUG port0 refstats set")
        if args.xstat1:
            snapshot = eval(args.xstat1)
            client.ports[1].get_xstats().reference_stats = snapshot
            print(u"DEBUG port1 refstats set")
        # Now we can call the official method to get differences.
        xstats0 = client.get_xstats(0)
        print(u"DEBUG port0 xstats got")
        xstats1 = client.get_xstats(1)
        print(u"DEBUG port1 xstats got")

    # If TRexError happens, let the script fail with stack trace.
    finally:
        client.clear_profile()
        print(u"DEBUG profile cleared")
        client.disconnect()
        print(u"DEBUG client disconnected")

    # TODO: check xstats format
    print(u"##### statistics port 0 #####")
    print(json.dumps(xstats0, indent=4, separators=(u",", u": ")))
    print(u"##### statistics port 1 #####")
    print(json.dumps(xstats1, indent=4, separators=(u",", u": ")))

    tx_0, rx_0 = xstats0[u"tx_good_packets"], xstats0[u"rx_good_packets"]
    tx_1, rx_1 = xstats1[u"tx_good_packets"], xstats1[u"rx_good_packets"]
    lost_a, lost_b = tx_0 - rx_1, tx_1 - rx_0

    print(f"packets lost from 0 --> 1:   {lost_a} pkts")
    print(f"packets lost from 1 --> 0:   {lost_b} pkts")

    total_rcvd, total_sent = rx_0 + rx_1, tx_0 + tx_1
    total_lost = total_sent - total_rcvd
    print(
        f"cps='unknown'; "
        f"total_received={total_rcvd}; "
        f"total_sent={total_sent}; "
        f"frame_loss={total_lost}; "
        f"latency_stream_0(usec)=-1/-1/-1; "
        f"latency_stream_1(usec)=-1/-1/-1; "
        f"latency_hist_stream_0=; "
        f"latency_hist_stream_1=; "
    )


if __name__ == u"__main__":
    print(u"DEBUG import success")
    main()
