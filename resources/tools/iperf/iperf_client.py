#!/usr/bin/python3

# Copyright (c) 2024 Cisco and/or its affiliates.
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
    if args.rate and not args.frame_size:
        # Linux default for TCP MSS (1460) matches 1518B frame size.
        args.frame_size = 1518
    if args.rate:
        headers = 18 + 20 + 20
        mss = args.frame_size - headers
        if mss < 88:
            raise RuntimeError(f"Linux requires at least 88: {mss=}")
        bitrate = mss * args.rate * 8 / args.instances / args.parallel
        # At low rates, avoid big bursts and switch to sending one by one.
        length = None if bitrate * 0.1 >= 128 * 1024 * 8 else mss

    processes = []
    outputs = []

    if args.async_start:
        args.duration += 999
    for i in range(args.instances):
        # TODO: Construct command on Robot machine using OptionString.
        cmd_list = ["exec", "sudo"]
        if args.namespace:
            cmd_list += ["ip", "netns", "exec", f"{args.namespace}"]
        cmd_list += ["iperf3"]
        cmd_list += ["--client", f"{args.host}"]
        cmd_list += ["--bind", f"{args.bind}"]
        if args.rate:
            cmd_list += ["--bitrate", f"{bitrate}"]
            cmd_list += ["--set-mss", f"{mss}"]
            if length:
                cmd_list += ["--length", f"{length}"]
        cmd_list += ["--port", f"{5201 + i}"]
        cmd_list += ["--parallel", f"{args.parallel}"]
        cmd_list += ["--time", f"{args.duration}"]
        if args.affinity:
            cmd_list += ["--affinity", f"{args.affinity[i]}"]
        if args.udp:
            cmd_list += ["--udp"]
        cmd_list += ["--zerocopy"]
        cmd_list += ["--json"]
        cmd = " ".join(cmd_list)
        processes.append(
            subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        )
    if args.async_start:
        for i in range(args.instances):
            print(processes[i].pid)
        return
    for i in range(args.instances):
        timeout = 2.0 + (0.0 if i else args.duration)
        stdout, stderr = processes[i].communicate(timeout=timeout)
        try:
            outputs.append(json.loads(stdout))
        except ValueError:
            raise RuntimeError(f"json error {stdout=} {stderr=}")
        outputs[i]["end"]["command"] = cmd
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
        type=float,  # Although iperf3 (v3.9) converts that to int.
        help="Duration of traffic run in seconds (-1=infinite).",
    )
    parser.add_argument(
        "--frame_size",
        required=False,
        type=int,
        help="Size of a Frame without padding and IPG. MSS is this minus 58.",
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
        default=8,
        type=int,
        help="The number of simultaneous client streams.",
    )

    args = parser.parse_args()

    # Currently limiting to uni- directional traffic.
    if args.traffic_directions != 1:
        print("Currently only uni- directional traffic is supported!")
        sys.exit(1)
    if args.affinity:
        aff_first, aff_last = args.affinity.split("-")
        args.affinity = list(range(int(aff_first), int(aff_last) + 1))
    simple_burst(args)


if __name__ == "__main__":
    main()
