#!/usr/bin/python3

# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""This module gets T-Rex advanced stateful (astf) traffic profile together
with other parameters, reads the profile and sends the traffic. At the end, it
parses for various counters.
"""

import argparse
import json
import sys
import time

sys.path.insert(
    0, u"/opt/trex-core-2.86/scripts/automation/trex_control_plane/interactive/"
)
from trex.astf.api import *


def fmt_latency(lat_min, lat_avg, lat_max, hdrh):
    """Return formatted, rounded latency.

    :param lat_min: Min latency
    :param lat_avg: Average latency
    :param lat_max: Max latency
    :param hdrh: Base64 encoded compressed HDRHistogram object.
    :type lat_min: str
    :type lat_avg: str
    :type lat_max: str
    :type hdrh: str
    :return: Formatted and rounded output (hdrh unchanged) "min/avg/max/hdrh".
    :rtype: str
    """
    try:
        t_min = int(round(float(lat_min)))
    except ValueError:
        t_min = int(-1)
    try:
        t_avg = int(round(float(lat_avg)))
    except ValueError:
        t_avg = int(-1)
    try:
        t_max = int(round(float(lat_max)))
    except ValueError:
        t_max = int(-1)

    return u"/".join(str(tmp) for tmp in (t_min, t_avg, t_max, hdrh))


def simple_burst(
        profile_file,
        duration,
        framesize,
        multiplier,
        port_0,
        port_1,
        latency,
        async_start=False,
        traffic_directions=2,
        send_delay=0.0,
        receive_delay=0.0,
    ):
    """Send traffic and measure packet loss and latency.

    Procedure:
     - reads the given traffic profile with streams,
     - connects to the T-rex astf client,
     - resets the ports,
     - removes all existing streams,
     - adds streams from the traffic profile to the ports,
     - clears the statistics from the client,
     - starts the traffic,
     - waits for the defined time (or runs forever if async mode is defined),
     - explicitly stops the traffic,
     - reads and displays the statistics and
     - disconnects from the client.

    Duration details:
    Contrary to stateless mode, ASTF profiles typically limit the number
    of flows/transactions that can happen.
    The caller is expected to set the duration parameter to idealized value,
    but set the two delay arguments when TRex is expected
    to start sending traffic late and finish processing replies even later.
    See *_traffic_duration output fields for TRex's measurement
    of the real traffic duration (should be without any inactivity overheads).
    If traffic has not ended by the final time, the traffic
    is stopped explicitly, counters reflect the state just after the stop.

    TODO: Support tests which focus only on some transaction phases,
    e.g. TCP tests ignoring init and teardown separated by delays.
    Currently, approximated time measures the whole traffic duration.

    :param profile_file: A python module with T-rex traffic profile.
    :param duration: Expected duration for all transactions to finish,
        without any TRex related delays, without even latency.
    :param framesize: Frame size.
    :param multiplier: Multiplier of profile CPS.
    :param port_0: Port 0 on the traffic generator.
    :param port_1: Port 1 on the traffic generator.
    :param latency: With latency stats.
    :param async_start: Start the traffic and exit.
    :param traffic_directions: Bidirectional (2) or unidirectional (1) traffic.
    :param send_delay: Time increase [s] for burst duration.
    :param receive_delay: Time increase [s] atop send_delay, for sleep duration.
        This includes latency.
    :type profile_file: str
    :type duration: float
    :type framesize: int or str
    :type multiplier: int
    :type port_0: int
    :type port_1: int
    :type latency: bool
    :type async_start: bool
    :type traffic_directions: int
    :type send_delay: float
    :type receive_delay: float
    """
    client = None
    total_received = 0
    total_sent = 0
    lost_a = 0
    lost_b = 0
    lat_a = u"-1/-1/-1/"
    lat_b = u"-1/-1/-1/"
    lat_a_hist = u""
    lat_b_hist = u""
    l7_data = u""
    stats = dict()
    approximated_duration = 0

    # Read the profile.
    try:
        # TODO: key-values pairs to the profile file
        #  - ips ?
        print(f"### Profile file:\n{profile_file}")
        profile = ASTFProfile.load(profile_file, framesize=framesize)
    except TRexError:
        print(f"Error while loading profile '{profile_file}'!")
        raise

    try:
        # Create the client.
        client = ASTFClient()
        # Connect to server
        client.connect()
        # Acquire ports, stop the traffic, remove loaded traffic and clear
        # stats.
        client.reset()
        # Load the profile.
        client.load_profile(profile)

        ports = [port_0]
        if traffic_directions > 1:
            ports.append(port_1)

        # Clear the stats before injecting.
        lost_a = 0
        lost_b = 0
        stats = dict()

        # Choose CPS and start traffic.
        client.start(
            mult=multiplier,
            # Increase the input duration slightly,
            # to ensure it does not end before sleep&stop below happens.
            duration=duration + send_delay,
            nc=True,
            latency_pps=int(multiplier) if latency else 0,
            client_mask=2**len(ports)-1,
        )
        time_start = time.monotonic()

        if async_start:
            # For async stop, we need to export the current snapshot.
            xsnap0 = client.ports[port_0].get_xstats().reference_stats
            print(f"Xstats snapshot 0: {xsnap0!r}")
            if traffic_directions > 1:
                xsnap1 = client.ports[port_1].get_xstats().reference_stats
                print(f"Xstats snapshot 1: {xsnap1!r}")
        else:
            time.sleep(duration + send_delay + receive_delay)
            # Do not block yet, the existing transactions may take long time
            # to finish. We need an action that is almost reset(),
            # but without clearing stats.
            client.stop(block=False)
            client.stop_latency()
            client.remove_rx_queue(client.get_all_ports())
            # Now we can wait for the real traffic stop.
            client.stop(block=True)

            # Read the stats after the traffic stopped (or time up).
            stats[time.monotonic() - time_start - delay] = client.get_stats(
                ports=ports
            )

            if client.get_warnings():
                for warning in client.get_warnings():
                    print(warning)

            # Now finish the complete reset.
            client.reset()

            print(u"##### Statistics #####")
            print(json.dumps(stats, indent=4, separators=(u",", u": ")))

            approximated_duration = list(sorted(stats.keys()))[-1]
            stats = stats[sorted(stats.keys())[-1]]
            lost_a = stats[port_0][u"opackets"] - stats[port_1][u"ipackets"]
            if traffic_directions > 1:
                lost_b = stats[port_1][u"opackets"] - stats[port_0][u"ipackets"]

            # TODO: Latency measurement not used at this phase. This part will
            #  be aligned in another commit.
            # Stats index is not a port number, but "pgid".
            if latency:
                lat_obj = stats[u"latency"][0][u"hist"]
                # TODO: Latency histogram is dictionary in astf mode,
                #  needs additional processing
                lat_a = fmt_latency(
                    str(lat_obj[u"min_usec"]), str(lat_obj[u"s_avg"]),
                    str(lat_obj[u"max_usec"]), u"-")
                lat_a_hist = str(lat_obj[u"histogram"])
                if traffic_directions > 1:
                    lat_obj = stats[u"latency"][1][u"hist"]
                    lat_b = fmt_latency(
                        str(lat_obj[u"min_usec"]), str(lat_obj[u"s_avg"]),
                        str(lat_obj[u"max_usec"]), u"-")
                    lat_b_hist = str(lat_obj[u"histogram"])

            if traffic_directions > 1:
                total_sent = \
                    stats[port_0][u"opackets"] + stats[port_1][u"opackets"]
                total_received = \
                    stats[port_0][u"ipackets"] + stats[port_1][u"ipackets"]
                client_sent = stats[port_0][u"opackets"]
                client_received = stats[port_0][u"ipackets"]
                client_stats = stats[u"traffic"][u"client"]
                server_stats = stats[u"traffic"][u"server"]
                # Some zero counters are not sent
                # Active and established flows UDP/TCP
                # Client
                c_act_flows = client_stats[u"m_active_flows"]
                c_est_flows = client_stats[u"m_est_flows"]
                c_traffic_duration = client_stats.get(u"m_traffic_duration", 0)
                l7_data = f"client_active_flows={c_act_flows}; "
                l7_data += f"client_established_flows={c_est_flows}; "
                l7_data += f"client_traffic_duration={c_traffic_duration}; "
                # Possible errors
                # Too many packets in NIC rx queue
                c_err_rx_throttled = client_stats.get(u"err_rx_throttled", 0)
                l7_data += f"client_err_rx_throttled={c_err_rx_throttled}; "
                # Number of client side flows that were not opened
                # due to flow-table overflow
                c_err_nf_throttled = client_stats.get(u"err_c_nf_throttled", 0)
                l7_data += f"client_err_nf_throttled={c_err_nf_throttled}; "
                # Too many flows
                c_err_flow_overflow = client_stats.get(u"err_flow_overflow", 0)
                l7_data += f"client_err_flow_overflow={c_err_flow_overflow}; "
                # Server
                s_act_flows = server_stats[u"m_active_flows"]
                s_est_flows = server_stats[u"m_est_flows"]
                s_traffic_duration = server_stats.get(u"m_traffic_duration", 0)
                l7_data += f"server_active_flows={s_act_flows}; "
                l7_data += f"server_established_flows={s_est_flows}; "
                l7_data += f"server_traffic_duration={s_traffic_duration}; "
                # Possible errors
                # Too many packets in NIC rx queue
                s_err_rx_throttled = server_stats.get(u"err_rx_throttled", 0)
                l7_data += f"client_err_rx_throttled={s_err_rx_throttled}; "
                if u"udp" in profile_file:
                    # Client
                    # Established connections
                    c_udp_connects = client_stats.get(u"udps_connects", 0)
                    l7_data += f"client_udp_connects={c_udp_connects}; "
                    # Closed connections
                    c_udp_closed = client_stats.get(u"udps_closed", 0)
                    l7_data += f"client_udp_closed={c_udp_closed}; "
                    # Sent bytes
                    c_udp_sndbyte = client_stats.get(u"udps_sndbyte", 0)
                    l7_data += f"client_udp_tx_bytes={c_udp_sndbyte}; "
                    # Sent packets
                    c_udp_sndpkt = client_stats.get(u"udps_sndpkt", 0)
                    l7_data += f"client_udp_tx_packets={c_udp_sndpkt}; "
                    # Received bytes
                    c_udp_rcvbyte = client_stats.get(u"udps_rcvbyte", 0)
                    l7_data += f"client_udp_rx_bytes={c_udp_rcvbyte}; "
                    # Received packets
                    c_udp_rcvpkt = client_stats.get(u"udps_rcvpkt", 0)
                    l7_data += f"client_udp_rx_packets={c_udp_rcvpkt}; "
                    # Keep alive drops
                    c_udp_keepdrops = client_stats.get(u"udps_keepdrops", 0)
                    l7_data += f"client_udp_keep_drops={c_udp_keepdrops}; "
                    # Client without flow
                    c_err_cwf = client_stats.get(u"err_cwf", 0)
                    l7_data += f"client_err_cwf={c_err_cwf}; "
                    # Server
                    # Accepted connections
                    s_udp_accepts = server_stats.get(u"udps_accepts", 0)
                    l7_data += f"server_udp_accepts={s_udp_accepts}; "
                    # Closed connections
                    s_udp_closed = server_stats.get(u"udps_closed", 0)
                    l7_data += f"server_udp_closed={s_udp_closed}; "
                    # Sent bytes
                    s_udp_sndbyte = server_stats.get(u"udps_sndbyte", 0)
                    l7_data += f"server_udp_tx_bytes={s_udp_sndbyte}; "
                    # Sent packets
                    s_udp_sndpkt = server_stats.get(u"udps_sndpkt", 0)
                    l7_data += f"server_udp_tx_packets={s_udp_sndpkt}; "
                    # Received bytes
                    s_udp_rcvbyte = server_stats.get(u"udps_rcvbyte", 0)
                    l7_data += f"server_udp_rx_bytes={s_udp_rcvbyte}; "
                    # Received packets
                    s_udp_rcvpkt = server_stats.get(u"udps_rcvpkt", 0)
                    l7_data += f"server_udp_rx_packets={s_udp_rcvpkt}; "
                elif u"tcp" in profile_file:
                    # Client
                    # Connection attempts
                    c_tcp_connattempt = client_stats.get(u"tcps_connattempt", 0)
                    l7_data += f"client_tcp_connattempt={c_tcp_connattempt}; "
                    # Established connections
                    c_tcp_connects = client_stats.get(u"tcps_connects", 0)
                    l7_data += f"client_tcp_connects={c_tcp_connects}; "
                    # Closed connections
                    c_tcp_closed = client_stats.get(u"tcps_closed", 0)
                    l7_data += f"client_tcp_closed={c_tcp_closed}; "
                    # Send bytes
                    c_tcp_sndbyte = client_stats.get(u"tcps_sndbyte", 0)
                    l7_data += f"client_tcp_tx_bytes={c_tcp_sndbyte}; "
                    # Received bytes
                    c_tcp_rcvbyte = client_stats.get(u"tcps_rcvbyte", 0)
                    l7_data += f"client_tcp_rx_bytes={c_tcp_rcvbyte}; "
                    # Server
                    # Accepted connections
                    s_tcp_accepts = server_stats.get(u"tcps_accepts", 0)
                    l7_data += f"server_tcp_accepts={s_tcp_accepts}; "
                    # Established connections
                    s_tcp_connects = server_stats.get(u"tcps_connects", 0)
                    l7_data += f"server_tcp_connects={s_tcp_connects}; "
                    # Closed connections
                    s_tcp_closed = server_stats.get(u"tcps_closed", 0)
                    l7_data += f"server_tcp_closed={s_tcp_closed}; "
                    # Sent bytes
                    s_tcp_sndbyte = server_stats.get(u"tcps_sndbyte", 0)
                    l7_data += f"server_tcp_tx_bytes={s_tcp_sndbyte}; "
                    # Received bytes
                    s_tcp_rcvbyte = server_stats.get(u"tcps_rcvbyte", 0)
                    l7_data += f"server_tcp_rx_bytes={s_tcp_rcvbyte}; "
            else:
                total_sent = stats[port_0][u"opackets"]
                total_received = stats[port_1][u"ipackets"]

            print(f"packets lost from {port_0} --> {port_1}: {lost_a} pkts")
            if traffic_directions > 1:
                print(f"packets lost from {port_1} --> {port_0}: {lost_b} pkts")

    except TRexError:
        print(u"T-Rex ASTF runtime error!", file=sys.stderr)
        raise

    finally:
        if client:
            if async_start:
                client.disconnect(stop_traffic=False, release_ports=True)
            else:
                client.clear_profile()
                client.disconnect()
                print(
                    f"multiplier={multiplier!r}; "
                    f"total_received={total_received}; "
                    f"total_sent={total_sent}; "
                    f"frame_loss={lost_a + lost_b}; "
                    f"approximated_duration={approximated_duration}; "
                    f"latency_stream_0(usec)={lat_a}; "
                    f"latency_stream_1(usec)={lat_b}; "
                    f"latency_hist_stream_0={lat_a_hist}; "
                    f"latency_hist_stream_1={lat_b_hist}; "
                    f"client_sent={client_sent}; "
                    f"client_received={client_received}; "
                    f"{l7_data}"
                )


def main():
    """Main function for the traffic generator using T-rex.

    It verifies the given command line arguments and runs "simple_burst"
    function.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        u"-p", u"--profile", required=True, type=str,
        help=u"Python traffic profile."
    )
    parser.add_argument(
        u"-d", u"--duration", required=True, type=float,
        help=u"Duration of the whole traffic run, including overheads."
    )
    parser.add_argument(
        u"-s", u"--frame_size", required=True,
        help=u"Size of a Frame without padding and IPG."
    )
    parser.add_argument(
        u"-m", u"--multiplier", required=True, type=float,
        help=u"Multiplier of profile CPS."
    )
    parser.add_argument(
        u"--port_0", required=True, type=int,
        help=u"Port 0 on the traffic generator."
    )
    parser.add_argument(
        u"--port_1", required=True, type=int,
        help=u"Port 1 on the traffic generator."
    )
    parser.add_argument(
        u"--async_start", action=u"store_true", default=False,
        help=u"Non-blocking call of the script."
    )
    parser.add_argument(
        u"--latency", action=u"store_true", default=False,
        help=u"Add latency stream."
    )
    parser.add_argument(
        u"--traffic_directions", type=int, default=2,
        help=u"Send bi- (2) or uni- (1) directional traffic."
    )
    parser.add_argument(
        u"--send_delay", required=True, type=float, default=0.0,
        help=u"Overhead for sending traffic, duration is increased by this [s]."
    )
    parser.add_argument(
        u"--receive_delay", required=True, type=float, default=0.0,
        help=u"Overhead for receiving traffic, sleep time is increased also by this [s]."
    )

    args = parser.parse_args()

    try:
        framesize = int(args.frame_size)
    except ValueError:
        framesize = args.frame_size

    simple_burst(
        profile_file=args.profile,
        duration=args.duration,
        framesize=framesize,
        multiplier=args.multiplier,
        port_0=args.port_0,
        port_1=args.port_1,
        latency=args.latency,
        async_start=args.async_start,
        traffic_directions=args.traffic_directions,
        send_delay=args.send_delay,
        receive_delay=args.receive_delay,
    )


if __name__ == u"__main__":
    main()
