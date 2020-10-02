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

def simple_burst(args):
    """Send traffic and measure throughput.

    :param args: Named arguments from command line.
    :type args: dict
    """
    if1_process = []
    if1_results = []
    cmd = None

    if args.rate and args.frame_size:
        iperf_frame_size = args.frame_size - 18
        iperf_rate = float(args.rate)
        bandwidth = \
            int(args.frame_size) * float(iperf_rate) / args.instances

    if args.warmup_time > 0:
        try:
            for i in range(0, args.instances):
                cmd = u"exec sudo "
                cmd += f"ip netns exec {args.namespace} " if args.namespace else u""
                cmd += f"iperf3 "
                cmd += f"--client {args.host} "
                cmd += f"--bind {args.bind} "
                if args.rate and args.frame_size:
                    cmd += f"--bandwidth {bandwidth} "
                    cmd += f"--length {iperf_frame_size} "
                cmd += f"--port {5201 + i} "
                cmd += f"--parallel {args.parallel} "
                cmd += f"--time {args.warmup_time} "
                if args.affinity:
                    cmd += f"--affinity {args.affinity} "
                if args.udp:
                    cmd += f"--udp "
                cmd += f"--zerocopy "
                cmd += f"--json"
                if1_process.append(
                    subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
                )
        finally:
            for i in range(0, args.instances):
                if1, _ = if1_process[i].communicate(
                    timeout=args.warmup_time + 60)

    if1_process = []
    if1_results = []
    cmd = None

    try:
        if args.async_start:
            args.duration += 999
        for i in range(0, args.instances):
            cmd = u"exec sudo "
            cmd += f"ip netns exec {args.namespace} " if args.namespace else u""
            cmd += f"iperf3 "
            cmd += f"--client {args.host} "
            cmd += f"--bind {args.bind} "
            if args.rate and args.frame_size:
                cmd += f"--bandwidth {bandwidth} "
                cmd += f"--length {iperf_frame_size} "
            cmd += f"--port {5201 + i} "
            cmd += f"--parallel {args.parallel} "
            cmd += f"--time {args.duration} "
            if args.affinity:
                cmd += f"--affinity {args.affinity} "
            if args.udp:
                cmd += f"--udp "
            cmd += f"--zerocopy "
            cmd += f"--json"
            if1_process.append(
                subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
            )
    finally:
        if args.async_start:
            for i in range(0, args.instances):
                print(if1_process[i].pid)
        else:
            for i in range(0, args.instances):
                if1, _ = if1_process[i].communicate(timeout=args.duration + 60)
                if1_results.append(json.loads(if1))
                if1_results[i][u"end"][u"command"] = cmd
                print(f"{json.dumps(if1_results[i]['end'], indent = 4)}")


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
        u"--host", required=True, type=str,
        help=u"Run in client mode, connecting to an iPerf server host."
    )
    parser.add_argument(
        u"--bind", required=True, type=str,
        help=u"Client bind IP address."
    )
    parser.add_argument(
        u"--udp", action=u"store_true", default=False,
        help=u"UDP test."
    )
    parser.add_argument(
        u"--affinity", required=False, type=str,
        help=u"Set the CPU affinity, if possible."
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
        u"--warmup_time", type=float, default=5.0,
        help=u"Traffic warm-up time in seconds, (0=disable)."
    )
    parser.add_argument(
        u"--async_start", action=u"store_true", default=False,
        help=u"Non-blocking call of the script."
    )
    parser.add_argument(
        u"--instances", default=1, type=int,
        help=u"The number of simultaneous client instances."
    )
    parser.add_argument(
        u"--parallel", default=8, type=int,
        help=u"The number of simultaneous client streams."
    )

    args = parser.parse_args()

    # Currently limiting to uni- directional traffic.
    if args.traffic_directions != 1:
        print(f"Currently only uni- directional traffic is supported!")
        sys.exit(1)

    simple_burst(args)


if __name__ == u"__main__":
    main()
