#!/usr/bin/python3

# Copyright (c) 2023 Cisco and/or its affiliates.
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
"""

import argparse
import json
import sys

from collections import OrderedDict  # Needed to parse xstats representation.

sys.path.insert(
    0, "/opt/trex-core-3.03/scripts/automation/trex_control_plane/interactive/"
)
from trex.astf.api import ASTFClient


def main():
    """Stop traffic if any is running. Report xstats."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--xstat", type=str, nargs="*", help="Reference xstat object if any."
    )
    args = parser.parse_args()

    client = ASTFClient()
    try:
        client.connect()
        client.acquire(force=True)
        client.stop()

        xstats = list()
        # Read the stats after the test,
        # we need to update values before the last trial started.
        for i in range(len(client.ports)):
            if args.xstat[i]:
                snapshot = eval(args.xstat[i])
                client.ports[i].get_xstats().reference_stats = snapshot
            # Now we can call the official method to get differences.
            xstats.append(client.get_xstats(i))
            print(f"##### statistics port {i} #####")
            print(json.dumps(xstats[i], indent=4, separators=(",", ": ")))
    finally:
        client.reset()
        client.disconnect()

    for idx,stat in enumerate(zip(xstats[0::2], xstats[1::2])):
        lost_r = stat[0]["tx_good_packets"] - stat[1]["rx_good_packets"]
        lost_l = stat[1]["tx_good_packets"] - stat[0]["rx_good_packets"]
        print(f"packets lost from {idx*2} --> {idx*2+1}:   {lost_r} pkts")
        print(f"packets lost from {idx*2+1} --> {idx*2}:   {lost_l} pkts")

    total_rcvd = 0
    total_sent = 0
    for stat in xstats:
        total_rcvd += stat["rx_good_packets"]
        total_sent += stat["tx_good_packets"]

    print(
        f"cps='unknown'; "
        f"total_received={total_rcvd}; "
        f"total_sent={total_sent}; "
        f"frame_loss={total_sent - total_rcvd}; "
        f"latency_stream_0(usec)=-1/-1/-1; "
        f"latency_stream_1(usec)=-1/-1/-1; "
        f"latency_hist_stream_0=; "
        f"latency_hist_stream_1=; "
    )


if __name__ == "__main__":
    main()
