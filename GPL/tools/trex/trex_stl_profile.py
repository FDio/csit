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

"""This module gets a traffic profile together with other parameters, reads
the profile and sends the traffic. At the end, it measures the packet loss and
latency.
"""

import argparse
import json
import sys
import time

sys.path.insert(
    0, "/opt/trex-core-3.03/scripts/automation/trex_control_plane/interactive/"
)
from trex.stl.api import STLClient, STLProfile, STLError


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

    return "/".join(str(tmp) for tmp in (t_min, t_avg, t_max, hdrh))


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
        delay=0.0,
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
    :param delay: Sleep overhead [s].
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
    :type delay: float
    """
    client = None
    total_rcvd = 0
    total_sent = 0
    approximated_duration = 0.0
    lat_a = "-1/-1/-1/"
    lat_b = "-1/-1/-1/"

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
        client.reset()
        client.remove_all_streams()

        if "macsrc" in profile_file:
            client.set_port_attr(promiscuous=True)
        if isinstance(framesize, int):
            last_stream_a = int((len(streams) - 2) / 2)
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
                print("##### FAILED to add latency streams #####")
                latency = False
        # Even for unidir, both ports are needed to see both rx and tx.
        ports = [port_0, port_1]

        # Clear the stats before injecting:
        client.clear_stats()

        # Choose rate and start traffic:
        client.start(
            ports=ports[:traffic_directions],
            mult=rate,
            duration=duration,
            force=force,
            core_mask=STLClient.CORE_MASK_PIN,
        )

        if async_start:
            # For async stop, we need to export the current snapshot.
            for i in range(len(client.ports)):
                xsnap = client.ports[i].get_xstats().reference_stats
                print(f"Xstats snapshot {i}: {xsnap!r}")
        else:
            time_start = time.monotonic()
            # wait_on_traffic fails if duration stretches by 30 seconds or more.
            # TRex has some overhead, wait some more.
            time.sleep(duration + delay)
            client.stop()
            time_stop = time.monotonic()
            approximated_duration = time_stop - time_start - delay
            # Read the stats after the traffic stopped (or time up).
            stats = client.get_stats()
            if client.get_warnings():
                for warning in client.get_warnings():
                    print(warning)
            # Now finish the complete reset.
            client.reset()

            print("##### Statistics #####")
            print(json.dumps(stats, indent=4, separators=(",", ": ")))

            nr_ports = len(client.ports)
            for i,j in zip(range(nr_ports)[0::2], range(nr_ports)[1::2]):
                lost_r = stats[i]["opackets"] - stats[j]["ipackets"]
                lost_l = stats[j]["opackets"] - stats[i]["ipackets"]
                print(f"packets lost from {i} --> {j}: {lost_r} pkts")
                print(f"packets lost from {j} --> {i}: {lost_l} pkts")

            # Stats index is not a port number, but "pgid".
            # We will take latency read from only first link.
            if latency:
                lat_obj = stats["latency"][0]["latency"]
                lat_a = fmt_latency(
                    str(lat_obj["total_min"]), str(lat_obj["average"]),
                    str(lat_obj["total_max"]), str(lat_obj["hdrh"]))
                # Do not bother with the other dir latency if unidir.
                if traffic_directions > 1:
                    lat_obj = stats["latency"][1]["latency"]
                    lat_b = fmt_latency(
                        str(lat_obj["total_min"]), str(lat_obj["average"]),
                        str(lat_obj["total_max"]), str(lat_obj["hdrh"]))

            total_rcvd = stats["total"]["ipackets"]
            total_sent = stats["total"]["opackets"]

    except STLError:
        print("T-Rex STL runtime error!", file=sys.stderr)
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
                f"frame_loss={total_sent - total_rcvd}; "
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
        "-p", "--profile", required=True, type=str,
        help="Python traffic profile."
    )
    parser.add_argument(
        "-d", "--duration", required=True, type=float,
        help="Duration of traffic run."
    )
    parser.add_argument(
        "-s", "--frame_size", required=True,
        help="Size of a Frame without padding and IPG."
    )
    parser.add_argument(
        "-r", "--rate", required=True,
        help="Traffic rate with included units (pps)."
    )
    parser.add_argument(
        "--port_0", required=True, type=int,
        help="Port 0 on the traffic generator."
    )
    parser.add_argument(
        "--port_1", required=True, type=int,
        help="Port 1 on the traffic generator."
    )
    parser.add_argument(
        "--async_start", action="store_true", default=False,
        help="Non-blocking call of the script."
    )
    parser.add_argument(
        "--latency", action="store_true", default=False,
        help="Add latency stream."
    )
    parser.add_argument(
        "--traffic_directions", type=int, default=2,
        help="Send bi- (2) or uni- (1) directional traffic."
    )
    parser.add_argument(
        "--force", action="store_true", default=False,
        help="Force start regardless of ports state."
    )
    parser.add_argument(
        "--delay", required=True, type=float, default=0.0,
        help="Delay assumed for traffic, sleep time is increased by this [s]."
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
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
