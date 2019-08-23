#!/usr/bin/python3

# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""This script uses T-REX stateless API to drive t-rex instance.

Requirements:
- T-REX: https://github.com/cisco-system-traffic-generator/trex-core
 - compiled and running T-REX process (eg. ./t-rex-64 -i)
 - trex.stl.api library
- Script must be executed on a node with T-REX instance

Functionality:
1. Stop any running traffic
"""

import sys
import json

sys.path.insert(0, "/opt/trex-core-2.54/scripts/automation/"+\
                   "trex_control_plane/interactive/")
from trex.stl.api import *


def main():
    """Stop traffic if any is running. Report xstats."""
    client = STLClient()
    try:
        # connect to server
        client.connect()

        client.acquire(force=True)
        # TODO: Support unidirection.
        client.stop(ports=[0, 1])

        # read the stats after the test
        xstats0 = client.get_xstats(0)
        xstats1 = client.get_xstats(1)

    # If STLError happens, let the script fail with stack trace.
    finally:
        client.disconnect()

    print("##### statistics port 0 #####")
    print(json.dumps(xstats0, indent=4, separators=(',', ': ')))
    print("##### statistics port 1 #####")
    print(json.dumps(xstats1, indent=4, separators=(',', ': ')))

    tx_0, rx_0 = xstats0["tx_good_packets"], xstats0["rx_good_packets"]
    tx_1, rx_1 = xstats1["tx_good_packets"], xstats1["rx_good_packets"]
    lost_a, lost_b = tx_0 - rx_1, tx_1 - rx_0

    print("\npackets lost from 0 --> 1:   {0} pkts".format(lost_a))
    print("packets lost from 1 --> 0:   {0} pkts".format(lost_b))

    total_rcvd, total_sent = rx_0 + rx_1, tx_0 + tx_1
    total_lost = total_sent - total_rcvd
    # TODO: Add latency.
    print(
        "rate='unknown', totalReceived={rec}, totalSent={sen}, frameLoss={los},"
        " latencyStream0(usec)=-1/-1/-1, latencyStream1(usec)=-1/-1/-1,"
        " targetDuration='manual'".format(
            rec=total_rcvd, sen=total_sent, los=total_lost))

if __name__ == "__main__":
    main()
