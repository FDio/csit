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

"""This module gets a traffic profile together with other parameters, reads
the profile and sends the traffic. At the end, it measures the packet loss and
latency.
"""

import argparse
import json
import sys
import time

sys.path.insert(
    0, u"/opt/trex-core-2.88/scripts/automation/trex_control_plane/interactive/"
)
from trex.stl.api import *


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
        rate,
        port_0,
        port_1,
        latency,
        async_start=False,
        traffic_directions=2,
        force=False,
    ):
    """Send traffic and measure packet loss and latency.

    Procedure:
     - reads the given traffic profile with streams,
     - connects to the T-rex client,
     - resets the ports,
     - removes all existing streams,
     - adds streams from the traffic profile to the ports,
     - if the warm-up time is more than 0, sends the warm-up traffic, reads the
       statistics,
     - clears the statistics from the client,
     - starts the traffic,
     - waits for the defined time (or runs forever if async mode is defined),
     - stops the traffic,
     - reads and displays the statistics and
     - disconnects from the client.

    :param profile_file: A python module with T-rex traffic profile.
    :param framesize: Frame size.
    :param duration: Duration of traffic run in seconds (-1=infinite).
    :param rate: Traffic rate [percentage, pps, bps].
    :param port_0: Port 0 on the traffic generator.
    :param port_1: Port 1 on the traffic generator.
    :param latency: With latency stats.
    :param async_start: Start the traffic and exit.
    :param traffic_directions: Bidirectional (2) or unidirectional (1) traffic.
    :param force: Force start regardless of ports state.
    :type profile_file: str
    :type framesize: int or str
    :type duration: float
    :type rate: str
    :type port_0: int
    :type port_1: int
    :type latency: bool
    :type async_start: bool
    :type traffic_directions: int
    :type force: bool
    """
    client = None
    total_rcvd = 0
    total_sent = 0
    approximated_duration = 0.0
    lost_a = 0
    lost_b = 0
    lat_a = u"-1/-1/-1/"
    lat_b = u"-1/-1/-1/"

    # Read the profile:
    try:
        print(f"### Profile file:\n{profile_file}")
        profile = STLProfile.load(
            profile_file, direction=0, port_id=0, framesize=framesize,
            rate=rate
        )
        streams = profile.get_streams()
    except STLError:
        print(f"Error while loading profile '{profile_file}'!")
        raise

    try:
        # Create the client:
        client = STLClient()
        # Connect to server:
        client.connect()
        # Prepare our ports (the machine has 0 <--> 1 with static route):
        client.reset(ports=[port_0, port_1])
        client.remove_all_streams(ports=[port_0, port_1])

        if u"macsrc" in profile_file:
            client.set_port_attr(ports=[port_0, port_1], promiscuous=True)
        if isinstance(framesize, int):
            last_stream_a = int((len(streams) - 2 ) / 2)
            last_stream_b = (last_stream_a * 2)
            client.add_streams(streams[0:last_stream_a], ports=[port_0])
            if traffic_directions > 1:
                client.add_streams(
                    streams[last_stream_a:last_stream_b], ports=[port_1])
        elif isinstance(framesize, str):
            client.add_streams(streams[0:3], ports=[port_0])
            if traffic_directions > 1:
                client.add_streams(streams[3:6], ports=[port_1])
        if latency:
            try:
                if isinstance(framesize, int):
                    client.add_streams(streams[last_stream_b], ports=[port_0])
                    if traffic_directions > 1:
                        client.add_streams(
                            streams[last_stream_b + 1], ports=[port_1])
                elif isinstance(framesize, str):
                    latency = False
            except STLError:
                # Disable latency if NIC does not support requested stream type
                print(u"##### FAILED to add latency streams #####")
                latency = False
        ports = [port_0]
        if traffic_directions > 1:
            ports.append(port_1)

        # Clear the stats before injecting:
        client.clear_stats()
        lost_a = 0
        lost_b = 0

        # Choose rate and start traffic:
        client.start(
            ports=ports,
            mult=rate,
            duration=duration,
            force=force,
            core_mask=STLClient.CORE_MASK_PIN,
        )

        if async_start:
            # For async stop, we need to export the current snapshot.
            xsnap0 = client.ports[0].get_xstats().reference_stats
            print(f"Xstats snapshot 0: {xsnap0!r}")
            if traffic_directions > 1:
                xsnap1 = client.ports[1].get_xstats().reference_stats
                print(f"Xstats snapshot 1: {xsnap1!r}")
        else:
            # Block until done:
            time_start = time.monotonic()
            client.wait_on_traffic(ports=ports, timeout=duration+30)
            time_stop = time.monotonic()
            approximated_duration = time_stop - time_start

            if client.get_warnings():
                for warning in client.get_warnings():
                    print(warning)

            # Read the stats after the test
            stats = client.get_stats()

            print(u"##### Statistics #####")
            print(json.dumps(stats, indent=4, separators=(u",", u": ")))

            lost_a = stats[port_0][u"opackets"] - stats[port_1][u"ipackets"]
            if traffic_directions > 1:
                lost_b = stats[port_1][u"opackets"] - stats[port_0][u"ipackets"]

            # Stats index is not a port number, but "pgid".
            if latency:
                lat_obj = stats[u"latency"][0][u"latency"]
                lat_a = fmt_latency(
                    str(lat_obj[u"total_min"]), str(lat_obj[u"average"]),
                    str(lat_obj[u"total_max"]), str(lat_obj[u"hdrh"]))
                if traffic_directions > 1:
                    lat_obj = stats[u"latency"][1][u"latency"]
                    lat_b = fmt_latency(
                        str(lat_obj[u"total_min"]), str(lat_obj[u"average"]),
                        str(lat_obj[u"total_max"]), str(lat_obj[u"hdrh"]))

            if traffic_directions > 1:
                total_sent = stats[0][u"opackets"] + stats[1][u"opackets"]
                total_rcvd = stats[0][u"ipackets"] + stats[1][u"ipackets"]
            else:
                total_sent = stats[port_0][u"opackets"]
                total_rcvd = stats[port_1][u"ipackets"]

            print(f"\npackets lost from {port_0} --> {port_1}: {lost_a} pkts")
            if traffic_directions > 1:
                print(f"packets lost from {port_1} --> {port_0}: {lost_b} pkts")

    except STLError:
        print(u"T-Rex STL runtime error!", file=sys.stderr)
        raise

    finally:
        if async_start:
            if client:
                client.disconnect(stop_traffic=False, release_ports=True)
        else:
            if client:
                client.disconnect()
            print(
                f"rate={rate!r}; "
                f"total_received={total_rcvd}; "
                f"total_sent={total_sent}; "
                f"frame_loss={lost_a + lost_b}; "
                f"target_duration={duration!r}; "
                f"approximated_duration={approximated_duration!r}; "
                f"latency_stream_0(usec)={lat_a}; "
                f"latency_stream_1(usec)={lat_b}; "
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
        help=u"Duration of traffic run."
    )
    parser.add_argument(
        u"-s", u"--frame_size", required=True,
        help=u"Size of a Frame without padding and IPG."
    )
    parser.add_argument(
        u"-r", u"--rate", required=True,
        help=u"Traffic rate with included units (pps)."
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
        u"--force", action=u"store_true", default=False,
        help=u"Force start regardless of ports state."
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
        rate=args.rate,
        port_0=args.port_0,
        port_1=args.port_1,
        latency=args.latency,
        async_start=args.async_start,
        traffic_directions=args.traffic_directions,
        force=args.force,
    )


if __name__ == u"__main__":
    main()
