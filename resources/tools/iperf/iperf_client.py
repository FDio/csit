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
the iPerf3 configuration and sends the traffic. At the end, it measures
the packet loss and latency.
"""

import argparse
import json
import sys
import time
import subprocess

def simple_burst(
        namespace=None, duration=1, frame_size=64, rate=1000, warmup_time=0.0,
        async_start=False, traffic_directions=1, instances=1, flows=1,
        udp=False, host=None, affinity=None):
    """Send traffic and measure throughput.

    :param namespace: Port netns name to run iPerf3 client on.
    :param duration: Duration of traffic run in seconds (-1=infinite).
    :param frame_size: Size of a Frame without padding and IPG.
    :param rate: Traffic rate with included units (pps).
    :param warmup_time: Traffic warm-up time in seconds, (0=disable).
    :param async_start: Start the traffic and exit.
    :param traffic_directions: Bidirectional (2) or unidirectional (1) traffic.
    :param instances: The number of simultaneous iPerf3 client instances.
    :param flows: The number of simultaneous connections to make to the server.
    :param udp: UDP test
    :param host: Run in client mode, connecting to an iPerf server.
    :param affinity: Set the CPU affinity, if possible.
    :type namespace: str
    :type duration: float
    :type frame_size: int or str
    :type rate: str
    :type warmup_time: float
    :type async_start: bool
    :type traffic_directions: int
    :type instances: int
    :type flows: int
    :type udp: bool
    :type host: str
    :type affinity: str
    """
    if1_process = []
    if1_results = []
    cmd = None

    if rate and frame_size:
        iperf_frame_size = frame_size - 18
        iperf_rate = float(rate[:-3]) if u"pps" in rate else float(rate)
        bandwidth = int(frame_size) * float(iperf_rate) / instances

    if warmup_time > 0:
        try:
            for inst in range(0, instances):
                cmd = u"exec sudo "
                cmd += f"ip netns exec {namespace} " if namespace else u""
                cmd += f"iperf3 "
                cmd += f"--client {host} "
                if rate and frame_size:
                    cmd += f"--bandwidth {bandwidth} "
                    cmd += f"--length {iperf_frame_size} "
                cmd += f"--port {5201 + inst} "
                cmd += f"--time {warmup_time} "
                if affinity:
                    cmd += f"--affinity {affinity} "
                if udp:
                    cmd += f"--udp "
                cmd += f"--zerocopy "
                cmd += f"--json"
                if1_process.append(
                    subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
                )
        finally:
            for inst in range(0, instances):
                if1, _ = if1_process[inst].communicate(timeout=warmup_time + 60)

    if1_process = []
    if1_results = []
    cmd = None

    try:
        if async_start:
            duration += 999
        for inst in range(0, instances):
            cmd = u"exec sudo "
            cmd += f"ip netns exec {namespace} " if namespace else u""
            cmd += f"iperf3 "
            cmd += f"--client {host} "
            if rate and frame_size:
                cmd += f"--bandwidth {bandwidth} "
                cmd += f"--length {iperf_frame_size} "
            cmd += f"--port {5201 + inst} "
            cmd += f"--time {duration} "
            cmd += f"--parallel 4 "
            if affinity:
                cmd += f"--affinity {affinity} "
            if udp:
                cmd += f"--udp "
            cmd += f"--zerocopy "
            cmd += f"--json"
            if1_process.append(
                subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
            )
    finally:
        if not async_start:
            for inst in range(0, instances):
                if1, _ = if1_process[inst].communicate(timeout=duration + 60)
                if1_results.append(json.loads(if1))
            if1_results[inst][u"end"][u"command"] = cmd
            print(f"{json.dumps(if1_results[inst]['end'], indent = 4)}")
        else:
            for inst in range(0, instances):
                print(if1_process[inst].pid)

def main():
    """Main function for the traffic generator using iPerf3.

    It verifies the given command line arguments and runs "simple_burst"
    function.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        u"--namespace", required=False, type=str,
        help=u"Port netns name to run iPerf client on."
    )
    parser.add_argument(
        u"--duration", required=True, type=float,
        help=u"Duration of traffic run in seconds (-1=infinite)."
    )
    parser.add_argument(
        u"--frame_size", required=False,
        help=u"Size of a Frame without padding and IPG."
    )
    parser.add_argument(
        u"--rate", required=False,
        help=u"Traffic rate with included units (pps)."
    )
    parser.add_argument(
        u"--traffic_directions", default=1, type=int,
        help=u"Send bi- (2) or uni- (1) directional traffic."
    )
    parser.add_argument(
        u"--instances", default=1, type=int,
        help=u"The number of simultaneous client instances."
    )
    parser.add_argument(
        u"--warmup_time", type=float, default=5.0,
        help=u"Traffic warm-up time in seconds, (0=disable)."
    )
    parser.add_argument(
        u"--async_start", action=u"store_true", default=False,
        help=u"Non-blocking call of the script."
    )
    parser.add_argument(
        u"--udp", action=u"store_true", default=False,
        help=u"UDP test."
    )
    parser.add_argument(
        u"--host", required=True, type=str,
        help=u"Run in client mode, connecting to an iPerf server host."
    )
    parser.add_argument(
        u"--affinity", required=False, type=str,
        help=u"Set the CPU affinity, if possible."
    )

    args = parser.parse_args()

    # Currently limiting to uni- directional traffic.
    if args.traffic_directions != 1:
        print(f"Currently only uni- directional traffic is supported!")
        sys.exit(1)

    simple_burst(
        namespace=args.namespace,
        duration=args.duration,
        frame_size=args.frame_size,
        rate=args.rate,
        warmup_time=args.warmup_time,
        async_start=args.async_start,
        traffic_directions=args.traffic_directions,
        instances=args.instances,
        udp=args.udp,
        host=args.host,
        affinity=args.affinity
    )

if __name__ == u"__main__":
    main()
