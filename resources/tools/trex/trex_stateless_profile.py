#!/usr/bin/python

# Copyright (c) 2017 Cisco and/or its affiliates.
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

import sys
import argparse
import json

sys.path.insert(0, "/opt/trex-core-2.35/scripts/automation/"
                   "trex_control_plane/stl/")

from trex_stl_lib.api import *


def fmt_latency(lat_min, lat_avg, lat_max):
    """Return formatted, rounded latency.

    :param lat_min: Min latency
    :param lat_avg: Average latency
    :param lat_max: Max latency
    :type lat_min: string
    :type lat_avg: string
    :type lat_max: string
    :return: Formatted and rounded output "min/avg/max"
    :rtype: string
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

    return "/".join(str(tmp) for tmp in (t_min, t_avg, t_max))


def simple_burst(profile_file, duration, framesize, rate, warmup_time, port_0,
                 port_1, latency, async_start=False):
    """Send the traffic and measure packet loss and latency.

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
    :param warmup_time: Traffic warm-up time in seconds, 0 = disable.
    :param port_0: Port 0 on the traffic generator.
    :param port_1: Port 1 on the traffic generator.
    :param latency: With latency stats.
    :param async_start: Start the traffic and exit.
    :type profile_file: str
    :type framesize: int or str
    :type duration: float
    :type rate: str
    :type warmup_time: float
    :type port_0: int
    :type port_1: int
    :type latency: boo;
    :type async_start: bool
    """

    client = None
    total_rcvd = 0
    total_sent = 0
    lost_a = 0
    lost_b = 0
    lat_a = "-1/-1/-1"
    lat_b = "-1/-1/-1"

    # Read the profile:
    try:
        print("### Profile file:\n{}".format(profile_file))
        profile = STLProfile.load(profile_file, direction=0, port_id=0,
                                  framesize=framesize)
        streams = profile.get_streams()
    except STLError as err:
        print("Error while loading profile '{0}' {1}".format(profile_file, err))
        sys.exit(1)

    try:
        # Create the client:
        client = STLClient(verbose_level=LoggerApi.VERBOSE_QUIET)
        # Connect to server:
        client.connect()
        # Prepare our ports (the machine has 0 <--> 1 with static route):
        client.reset(ports=[port_0, port_1])
        client.remove_all_streams(ports=[port_0, port_1])

        if "macsrc" in profile_file:
            client.set_port_attr(ports=[port_0, port_1], promiscuous=True,
                                 resolve=False)
        if isinstance(framesize, int):
            client.add_streams(streams[0], ports=[port_0])
            client.add_streams(streams[1], ports=[port_1])
        elif isinstance(framesize, str):
            client.add_streams(streams[0:3], ports=[port_0])
            client.add_streams(streams[3:6], ports=[port_1])
        if latency:
            try:
                if isinstance(framesize, int):
                    client.add_streams(streams[2], ports=[port_0])
                    client.add_streams(streams[3], ports=[port_1])
                elif isinstance(framesize, str):
                    latency = False
            except STLError:
                # Disable latency if NIC does not support requested stream type
                print("##### FAILED to add latency streams #####")
                latency = False
        # Warm-up phase:
        if warmup_time > 0:
            # Clear the stats before injecting:
            client.clear_stats()

            # Choose rate and start traffic:
            client.start(ports=[port_0, port_1], mult=rate,
                         duration=warmup_time)

            # Block until done:
            client.wait_on_traffic(ports=[port_0, port_1],
                                   timeout=warmup_time+30)

            if client.get_warnings():
                for warning in client.get_warnings():
                    print(warning)

            # Read the stats after the test:
            stats = client.get_stats()

            print("##### Warmup statistics #####")
            print(json.dumps(stats, indent=4, separators=(',', ': '),
                             sort_keys=True))

            lost_a = stats[0]["opackets"] - stats[1]["ipackets"]
            lost_b = stats[1]["opackets"] - stats[0]["ipackets"]

            print("\npackets lost from 0 --> 1: {0} pkts".format(lost_a))
            print("packets lost from 1 --> 0: {0} pkts".format(lost_b))

        # Clear the stats before injecting:
        client.clear_stats()
        lost_a = 0
        lost_b = 0

        # Choose rate and start traffic:
        client.start(ports=[port_0, port_1], mult=rate, duration=duration)

        if not async_start:
            # Block until done:
            client.wait_on_traffic(ports=[port_0, port_1], timeout=duration+30)

            if client.get_warnings():
                for warning in client.get_warnings():
                    print(warning)

            # Read the stats after the test
            stats = client.get_stats()

            print("##### Statistics #####")
            print(json.dumps(stats, indent=4, separators=(',', ': '),
                             sort_keys=True))

            lost_a = stats[0]["opackets"] - stats[1]["ipackets"]
            lost_b = stats[1]["opackets"] - stats[0]["ipackets"]

            if latency:
                lat_a = fmt_latency(
                    str(stats["latency"][0]["latency"]["total_min"]),
                    str(stats["latency"][0]["latency"]["average"]),
                    str(stats["latency"][0]["latency"]["total_max"]))
                lat_b = fmt_latency(
                    str(stats["latency"][1]["latency"]["total_min"]),
                    str(stats["latency"][1]["latency"]["average"]),
                    str(stats["latency"][1]["latency"]["total_max"]))

            total_sent = stats[0]["opackets"] + stats[1]["opackets"]
            total_rcvd = stats[0]["ipackets"] + stats[1]["ipackets"]

            print("\npackets lost from 0 --> 1:   {0} pkts".format(lost_a))
            print("packets lost from 1 --> 0:   {0} pkts".format(lost_b))

    except STLError as err:
        sys.stderr.write("{0}\n".format(err))
        sys.exit(1)

    finally:
        if async_start:
            if client:
                client.disconnect(stop_traffic=False, release_ports=True)
        else:
            if client:
                client.disconnect()
            print("rate={0}, totalReceived={1}, totalSent={2}, "
                  "frameLoss={3}, latencyStream0(usec)={4}, "
                  "latencyStream1(usec)={5}".
                  format(rate, total_rcvd, total_sent, lost_a + lost_b,
                         lat_a, lat_b))


def main():
    """Main function for the traffic generator using T-rex.

    It verifies the given command line arguments and runs "simple_burst"
    function.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--profile",
                        required=True,
                        type=str,
                        help="Python traffic profile.")
    parser.add_argument("-d", "--duration",
                        required=True,
                        type=float,
                        help="Duration of traffic run.")
    parser.add_argument("-s", "--frame_size",
                        required=True,
                        help="Size of a Frame without padding and IPG.")
    parser.add_argument("-r", "--rate",
                        required=True,
                        help="Traffic rate with included units (%, pps).")
    parser.add_argument("-w", "--warmup_time",
                        type=float,
                        default=5.0,
                        help="Traffic warm-up time in seconds, 0 = disable.")
    parser.add_argument("--port_0",
                        required=True,
                        type=int,
                        help="Port 0 on the traffic generator.")
    parser.add_argument("--port_1",
                        required=True,
                        type=int,
                        help="Port 1 on the traffic generator.")
    parser.add_argument("--async",
                        action="store_true",
                        default=False,
                        help="Non-blocking call of the script.")
    parser.add_argument("--latency",
                        action="store_true",
                        default=False,
                        help="Add latency stream")
    args = parser.parse_args()

    try:
        framesize = int(args.frame_size)
    except ValueError:
        framesize = args.frame_size

    simple_burst(profile_file=args.profile,
                 duration=args.duration,
                 framesize=framesize,
                 rate=args.rate,
                 warmup_time=args.warmup_time,
                 port_0=args.port_0,
                 port_1=args.port_1,
                 latency=args.latency,
                 async_start=args.async)


if __name__ == '__main__':
    main()
