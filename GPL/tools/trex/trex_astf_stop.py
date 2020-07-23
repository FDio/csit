#!/usr/bin/python3

# Copyright (c) 2020 Cisco and/or its affiliates.
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

from collections import OrderedDict  # Needed to parse xstats representation.

sys.path.insert(
    0, u"/opt/trex-core-2.73/scripts/automation/trex_control_plane/interactive/"
)
from trex.astf.api import *


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

    client = ASTFClient()
    try:
        # connect to server
        client.connect()

        client.acquire(force=True)
        client.stop()

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

    # If TRexError happens, let the script fail with stack trace.
    finally:
        client.clear_profile()
        client.disconnect()

    # TODO: check xstats format
    print(u"##### statistics port 0 #####")
    print(json.dumps(xstats0, indent=4, separators=(u",", u": ")))
    print(u"##### statistics port 1 #####")
    print(json.dumps(xstats1, indent=4, separators=(u",", u": ")))

    tx_0, rx_0 = xstats0[u"tx_good_packets"], xstats0[u"rx_good_packets"]
    tx_1, rx_1 = xstats1[u"tx_good_packets"], xstats1[u"rx_good_packets"]
    lost_a, lost_b = tx_0 - rx_1, tx_1 - rx_0

    client_stats = xstats0[u"traffic"][u"client"]
    server_stats = xstats1[u"traffic"][u"server"]
    # Active and established flows UDP/TCP
    # Client
    c_act_flows = client_stats[u"m_active_flows"]
    c_est_flows = client_stats[u"m_est_flows"]
    l7_data = f"client_active_flows={c_act_flows}, "
    l7_data += f"client_established_flows={c_est_flows}, "
    # Server
    s_act_flows = server_stats[u"m_active_flows"]
    s_est_flows = server_stats[u"m_est_flows"]
    l7_data += f"server_active_flows={s_act_flows}, "
    l7_data += f"server_established_flows={s_est_flows}, "
    # Some zero counters are not sent
    # Client
    # Established connections
    c_udp_connects = client_stats.get(u"udps_connects", 0)
    l7_data += f"client_udp_connects={c_udp_connects}, "
    # Closed connections
    c_udp_closed = client_stats.get(u"udps_closed", 0)
    l7_data += f"client_udp_closed={c_udp_closed}, "
    # Server
    # Accepted connections
    s_udp_accepts = server_stats.get(u"udps_accepts", 0)
    l7_data += f"server_udp_accepts={s_udp_accepts}, "
    # Closed connections
    s_udp_closed = server_stats.get(u"udps_closed", 0)
    # Client
    # Initiated connections
    c_tcp_connatt = client_stats.get(u"tcps_connattempt", 0)
    l7_data += f"client_tcp_connect_inits={c_tcp_connatt}, "
    # Established connections
    c_tcp_connects = client_stats.get(u"tcps_connects", 0)
    l7_data += f"client_tcp_connects={c_tcp_connects}, "
    # Closed connections
    c_tcp_closed = client_stats.get(u"tcps_closed", 0)
    l7_data += f"client_tcp_closed={c_tcp_closed}, "
    # Server
    # Accepted connections
    s_tcp_accepts = server_stats.get(u"tcps_accepts", 0)
    l7_data += f"server_tcp_accepts={s_tcp_accepts}, "
    # Established connections
    s_tcp_connects = server_stats.get(u"tcps_connects", 0)
    l7_data += f"server_tcp_connects={s_tcp_connects}, "
    # Closed connections
    s_tcp_closed = server_stats.get(u"tcps_closed", 0)
    l7_data += f"server_tcp_closed={s_tcp_closed}, "

    print(f"packets lost from 0 --> 1:   {lost_a} pkts")
    print(f"packets lost from 1 --> 0:   {lost_b} pkts")

    total_rcvd, total_sent = rx_0 + rx_1, tx_0 + tx_1
    total_lost = total_sent - total_rcvd
    # TODO: Add latency.
    print(
        f"cps='unknown', total_received={total_rcvd}, total_sent={total_sent}, "
        f"frame_loss={total_lost}, "
        f"latency_stream_0(usec)=-1/-1/-1, latency_stream_1(usec)=-1/-1/-1, "
        u"latency_hist_stream_0={}, latency_hist_stream_1={}, "
        f"{l7_data}"
    )


if __name__ == u"__main__":
    main()
