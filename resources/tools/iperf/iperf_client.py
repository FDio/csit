#!/usr/bin/python3

# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""This script gets a bandwith limit together with other parameters, reads
the iPerf3 configuration and sends the traffic. At the end, it measures
the packet loss and latency.
"""

import argparse
import json
import sys
import subprocess


def simple_burst(args):
    """Send traffic and measure throughput.

    :param args: Named arguments from command line.
    :type args: dict
    """
    if args.rate and args.frame_size:
        mss = args.frame_size - 18
        bitrate = mss * args.rate * 8 / args.instances

    processes = []
    outputs = []

    if args.async_start:
        args.duration += 999
    for i in range(args.instances):
        cmd_list = ["exec", "sudo"]
        if args.namespace:
            cmd_list += ["ip", "netns", "exec", f"{args.namespace}"]
        cmd_list += ["iperf3"]
        cmd_list += ["--client", f"{args.host}"]
        cmd_list += ["--bind", f"{args.bind}"]
        if args.rate and args.frame_size:
            cmd_list += ["--bitrate", f"{bitrate}"]
            cmd_list += ["--set-mss", f"{mss}"]
            cmd_list += ["--length", f"{mss}"]
        cmd_list += ["--port", f"{5201 + i}"]
        cmd_list += ["--parallel", f"{args.parallel}"]
        cmd_list += ["--time", f"{args.duration}"]
        if args.affinity:
            cmd_list += ["--affinity", f"{args.affinity}"]
        if args.udp:
            cmd_list += ["--udp"]
        cmd_list += ["--zerocopy"]
        cmd_list += ["--json"]
        processes.append(
            subprocess.Popen([" ".join(cmd_list)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        )
    if args.async_start:
        for i in range(args.instances):
            print(processes[i].pid)
            print(f"{cmd_list=}", file=sys.stderr)
        return
    for i in range(args.instances):
        timeout = 1.0 if i else args.duration + 60
        stdout, stderr = processes[i].communicate(timeout=timeout)
        print(f"from process {i}: {stderr}", file=sys.stderr)
        print(f"rc={processes[i].returncode}", file=sys.stderr)
        outputs.append(json.loads(stdout))
        outputs[i]["end"]["command"] = cmd_list
        print(f"{json.dumps(outputs[i]['end'], indent = 4)}")


def main():
    """Main function for the traffic generator using iPerf3.

    It verifies the given command line arguments and runs "simple_burst"
    function.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--namespace",
        required=False,
        type=str,
        help="Port netns name to run iPerf client on.",
    )
    parser.add_argument(
        "--host",
        required=True,
        type=str,
        help="Run in client mode, connecting to an iPerf server host.",
    )
    parser.add_argument(
        "--bind",
        required=True,
        type=str,
        help="Client bind IP address.",
    )
    parser.add_argument(
        "--udp",
        action="store_true",
        default=False,
        help="UDP test.",
    )
    parser.add_argument(
        "--affinity",
        required=False,
        type=str,
        help="Set the CPU affinity, if possible.",
    )
    parser.add_argument(
        "--duration",
        required=True,
        type=float,
        help="Duration of traffic run in seconds (-1=infinite).",
    )
    parser.add_argument(
        "--frame_size",
        required=False,
        type=int,
        help="Size of a Frame without padding and IPG.",
    )
    parser.add_argument(
        "--rate",
        required=False,
        type=float,
        help="Traffic rate without included units (pps).",
    )
    parser.add_argument(
        "--traffic_directions",
        default=1,
        type=int,
        help="Send bi- (2) or uni- (1) directional traffic.",
    )
    parser.add_argument(
        "--async_start",
        action="store_true",
        default=False,
        help="Non-blocking call of the script.",
    )
    parser.add_argument(
        "--instances",
        default=1,
        type=int,
        help="The number of simultaneous client instances.",
    )
    parser.add_argument(
        "--parallel",
        #default=8,
        default=1,
        type=int,
        help="The number of simultaneous client streams.",
    )

    args = parser.parse_args()

    # Currently limiting to uni- directional traffic.
    if args.traffic_directions != 1:
        print("Currently only uni- directional traffic is supported!")
        sys.exit(1)

    simple_burst(args)


if __name__ == "__main__":
    main()
