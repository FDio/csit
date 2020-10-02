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

"""This module gets a bandwith limit together with other parameters, reads
the server ip address and sends the traffic. At the end, it measures the packet
loss and latency.
"""

import argparse
import configparser
import json
import sys
import time
import subprocess

def simple_burst(
        port_0_netns, port_1_netns, duration, frame_size, rate, warmup_time,
        async_start=False, traffic_directions=2, flows=10, base_port=5201):

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
    :param warmup_time: Traffic warm-up time in seconds, 0 = disable.
    :param port_0: Port 0 on the traffic generator.
    :param port_1: Port 1 on the traffic generator.
    :param latency: With latency stats.
    :param async_start: Start the traffic and exit.
    :param traffic_directions: Bidirectional (2) or unidirectional (1) traffic.
    :param force: Force start regardless of ports state.
    :param ip_profile: IP profile for traffic profile.
    :type profile_file: str
    :type framesize: int or str
    :type duration: float
    :type rate: str
    :type warmup_time: float
    :type port_0: int
    :type port_1: int
    :type latency: bool
    :type async_start: bool
    :type traffic_directions: int
    :type force: bool
    :type ip_profile: str
    """
    total_rcvd = 0
    total_sent = 0
    lost_a = 0
    lost_b = 0
    sp_if1 = []
    sp_if2 = []
    iperf_if1_result = []
    iperf_if2_result = []
    # Read the config:
    iperf_config = configparser.ConfigParser()
    try:
        print(f"### iPerf config file:\n")
        iperf_config.read('/tmp/iperf.conf')
        iperf_server_if1_addr = iperf_config.get('server', 'IF1_IP')
        iperf_server_if2_addr = iperf_config.get('server', 'IF2_IP')
    except configparser.Error as err:
        print(f"Error while loading iperf config. {err!r}")
        sys.exit(1)

    iperf_frame_size = frame_size - 18
    iperf_rate = float(rate[:-3]) if u"pps" in rate else float(rate)
    bandwidth = int(frame_size) * float(iperf_rate) / flows

    try:
        for inst in range(0, flows):
            iperf_port = base_port + inst
            iperf_if1_cmd = \
                f"sudo ip netns exec {port_0_netns} iperf3 "\
                f"-c {iperf_server_if2_addr} -b {bandwidth} -u -N -w 64K "\
                f"-l {iperf_frame_size} -t {duration} -Z -p {iperf_port} "\
                f"--json"
            iperf_if2_cmd = \
                f"sudo ip netns exec {port_1_netns} iperf3 "\
                f"-c {iperf_server_if1_addr} -b {bandwidth} -u -N -w 64K "\
                f"-l {iperf_frame_size} -t {duration} -Z -p {iperf_port} "\
                f"--json"
            if traffic_directions == 0 or traffic_directions == 2:
                sp_if1.append(subprocess.Popen([iperf_if1_cmd], shell=True, \
                    stdout=subprocess.PIPE))
            if traffic_directions == 1 or traffic_directions == 2:
                sp_if2.append(subprocess.Popen([iperf_if2_cmd], shell=True, \
                    stdout=subprocess.PIPE))
    finally:
        print('#### Statistics ####')
        for inst in range(0, flows):
             (output_if1, _) = sp_if1[inst].communicate(timeout=duration + 10)
             (output_if2, _) = sp_if2[inst].communicate(timeout=duration + 10)
             iperf_if1_result.append(json.loads(output_if1))
             iperf_if2_result.append(json.loads(output_if2))
             print(f"Instance: {inst}")
             print(json.dumps(iperf_if1_result[inst]['end']['sum'], indent = 4))
             total_rcvd = total_rcvd + \
                 iperf_if1_result[inst]['end']['sum']['packets'] + \
                 iperf_if2_result[inst]['end']['sum']['packets']
             lost_a = lost_a + iperf_if1_result[inst]['end']['sum']['lost_packets']
             lost_b = lost_b + iperf_if2_result[inst]['end']['sum']['lost_packets']
             total_sent = total_rcvd + lost_a + lost_b
             lat_a = iperf_if1_result[inst]['end']['sum']['jitter_ms']
             lat_b = iperf_if2_result[inst]['end']['sum']['jitter_ms']

        print(
            f"rate={rate!r}, totalReceived={total_rcvd}, "
            f"totalSent={total_sent}, frameLoss={lost_a + lost_b}, "
            f"latencyStream0(usec)={lat_a}, latencyStream1(usec)={lat_b}, "
            f"targetDuration={duration!r}"
        )


def main():
    """Main function for the traffic generator using iPerf.

    It verifies the given command line arguments and runs "simple_burst"
    function.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        u"--port_0_netns", required=True, type=str,
        help=u"Port 0 netns name on traffic generator."
    )
    parser.add_argument(
        u"--port_1_netns", required=True, type=str,
        help=u"Port 1 netns name on the traffic generator."
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
        u"--traffic_directions", type=int, default=2,
        help=u"Send bi- (2) or uni- (1) directional traffic."
    )
    parser.add_argument(
        u"--base_port", type=int, default=5201,
        help=u"iPerf base port."
    )
    parser.add_argument(
        u"-p", u"--flows", type=int, default=10,
        help=u"Number of traffic flows."
    )
    parser.add_argument(
        u"-w", u"--warmup_time", type=float, default=5.0,
        help=u"Traffic warm-up time in seconds, 0 = disable."
    )
    parser.add_argument(
        u"--async_start", action=u"store_true", default=False,
        help=u"Non-blocking call of the script."
    )

    args = parser.parse_args()

    try:
        frame_size = int(args.frame_size)
    except ValueError:
        frame_size = args.frame_size

    simple_burst(
        port_0_netns=args.port_0_netns, port_1_netns=args.port_1_netns,
        duration=args.duration, frame_size=frame_size, rate=args.rate,
        warmup_time=args.warmup_time, async_start=args.async_start,
        traffic_directions=args.traffic_directions, base_port=args.base_port,
        flows=args.flows
    )

if __name__ == u"__main__":
    main()
