#!/usr/bin/python

# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""This script uses T-REX stateless API to drive t-rex instance.

Requirements:
- T-REX: https://github.com/cisco-system-traffic-generator/trex-core
 - compiled and running T-REX process (eg. ./t-rex-64 -i -c 4)
 - trex_stl_lib.api library
- Script must be executed on a node with T-REX instance
- 2 interfaces must be configured in configuretion file /etc/trex_cfg.yaml

##################### Example of /etc/trex_cfg.yaml ##########################
- port_limit      : 2 # numbers of ports to use
  version         : 2
  interfaces      : ["84:00.0","84:00.1"] # PCI address of interfaces
  port_info       :  # set eth mac addr
          - dest_mac        :   [0x90,0xe2,0xba,0x1f,0x97,0xd5]  # port 0
            src_mac         :   [0x90,0xe2,0xba,0x1f,0x97,0xd4]
          - dest_mac        :   [0x90,0xe2,0xba,0x1f,0x97,0xd4]  # port 1
            src_mac         :   [0x90,0xe2,0xba,0x1f,0x97,0xd5]
##############################################################################

Functionality:
1. Configure traffic on running T-REX instance
2. Clear statistics on all ports
3. Ctart traffic with specified duration
4. Print statistics to stdout

"""

import argparse
import json
import socket
import string
import struct
import sys

sys.path.insert(0, "/opt/trex-core-2.06/scripts/automation/"+\
                   "trex_control_plane/stl/")
from trex_stl_lib.api import *

stream_table = {'IMIX_v4_1': [{'size': 64, 'pps': 28, 'isg':0},
                              {'size': 570, 'pps': 16, 'isg':0.1},
                              {'size': 1518, 'pps': 4, 'isg':0.2}]
               }

def generate_payload(length):
    """Generate payload.

    :param length: Length of payload.
    :type length: int
    :return: Payload filled with chars.
    :rtype string
    """

    word = ''
    alphabet_size = len(string.letters)
    for i in range(length):
        word += string.letters[(i % alphabet_size)]

    return word


def get_start_end_ipv6(start_ip, end_ip):
    """Get start and end host from IPv6 as integer.

    :param start_ip: Start IPv6.
    :param end_ip: End IPv6.
    :type start_ip: string
    :type end_ip: string
    :return: Start host, end host.
    :rtype int
    """

    try:
        ip1 = socket.inet_pton(socket.AF_INET6, start_ip)
        ip2 = socket.inet_pton(socket.AF_INET6, end_ip)

        hi1, lo1 = struct.unpack('!QQ', ip1)
        hi2, lo2 = struct.unpack('!QQ', ip2)

        if ((hi1 << 64) | lo1) > ((hi2 << 64) | lo2):
            print "IPv6: start_ip is greater then end_ip"
            sys.exit(2)

        max_p1 = abs(int(lo1) - int(lo2))
        base_p1 = lo1
    except AddressValueError as ex_error:
        print ex_error
        sys.exit(2)

    return base_p1, max_p1

def create_streams_v46(base_pkt_a, base_pkt_b, vm1, vm2, frame_size):
    """Create STLStream streams

    :param base_pkt_a: Base packet a for stream_a
    :param base_pkt_b: Base packet b for stream_b
    :param vm1: vm for stream_a
    :param vm2: vm for stream_b
    :param frame_size: frame size or name of traffic profile
    :type base_pkt_a: Eth (scapy)
    :type base_pkt_b: Eth (scapy)
    :type vm1: STLScVmRaw
    :type vm2: STLScVmRaw
    :frame_size: int or string
    :return: stream_a, stream_b, stream_a_latency, stream_b_latency
    :rtype: STLStream, STLStream, STLStream, STLStream
    """

    if type(frame_size) is int:

        fsize_no_fcs = frame_size - 4 # no FCS
        pkt_a = STLPktBuilder(pkt=base_pkt_a/generate_payload(
            max(0, fsize_no_fcs-len(base_pkt_a))), vm=vm1)
        pkt_b = STLPktBuilder(pkt=base_pkt_b/generate_payload(
            max(0, fsize_no_fcs-len(base_pkt_b))), vm=vm2)
        pkt_lat_a = STLPktBuilder(pkt=base_pkt_a/generate_payload(
            max(0, fsize_no_fcs-len(base_pkt_a))))
        pkt_lat_b = STLPktBuilder(pkt=base_pkt_b/generate_payload(
            max(0, fsize_no_fcs-len(base_pkt_b))))
        lat_stream1 = STLStream(packet=pkt_lat_a,
                                flow_stats=STLFlowLatencyStats(pg_id=0),
                                mode=STLTXCont(pps=1000))
        # second traffic stream with a phase of 10ns (inter stream gap)
        lat_stream2 = STLStream(packet=pkt_lat_b,
                                isg=10.0,
                                flow_stats=STLFlowLatencyStats(pg_id=1),
                                mode=STLTXCont(pps=1000))

        stream1 = STLStream(packet=pkt_a,
                            mode=STLTXCont(pps=1000))
        # second traffic stream with a phase of 10ns (inter stream gap)
        stream2 = STLStream(packet=pkt_b,
                            isg=10.0,
                            mode=STLTXCont(pps=1000))
    elif type(frame_size) is str:
        lat_stream1 = []
        lat_stream2 = []
        stream1 = []
        stream2 = []

        for x in stream_table[frame_size]:
            fsize_no_fcs = x['size'] - 4 # no FCS
            pkt_a = STLPktBuilder(pkt=base_pkt_a/generate_payload(
                max(0, fsize_no_fcs-len(base_pkt_a))), vm=vm1)
            pkt_b = STLPktBuilder(pkt=base_pkt_b/generate_payload(
                max(0, fsize_no_fcs-len(base_pkt_b))), vm=vm2)

            stream1.append(STLStream(packet=pkt_a,
                               isg=x['isg'],
                               mode=STLTXCont(pps=x['pps'])))
            stream2.append(STLStream(packet=pkt_b,
                               isg=x['isg'],
                               mode=STLTXCont(pps=x['pps'])))

    else:
        raise ValueError("Unknown frame_size type")

    return (stream1, stream2, lat_stream1, lat_stream2)

def create_streams(traffic_options, frame_size=64):
    """Create two IP packets to be used in stream.

    :param traffic_options: Parameters for packets.
    :param frame_size: Size of L2 frame.
    :type traffic_options: list
    :type frame_size: int
    :return: Packet instances.
    :rtype: Tuple of STLPktBuilder
    """

    if type(frame_size) is int and frame_size < 64:
        print_error("Frame min. size is 64B")
        sys.exit(1)

    p1_src_start_ip = traffic_options['p1_src_start_ip']
    p1_src_end_ip = traffic_options['p1_src_end_ip']
    p1_dst_start_ip = traffic_options['p1_dst_start_ip']
    p2_src_start_ip = traffic_options['p2_src_start_ip']
    p2_src_end_ip = traffic_options['p2_src_end_ip']
    p2_dst_start_ip = traffic_options['p2_dst_start_ip']

    base_pkt_a = Ether()/IP(src=p1_src_start_ip, dst=p1_dst_start_ip, proto=61)
    base_pkt_b = Ether()/IP(src=p2_src_start_ip, dst=p2_dst_start_ip, proto=61)

    # The following code applies raw instructions to packet (IP src increment).
    # It splits the generated traffic by "ip_src" variable to cores and fix
    # IPv4 header checksum.
    vm1 = STLScVmRaw([STLVmFlowVar(name="src",
                                   min_value=p1_src_start_ip,
                                   max_value=p1_src_end_ip,
                                   size=4, op="inc"),
                      STLVmWrFlowVar(fv_name="src", pkt_offset="IP.src"),
                      STLVmFixIpv4(offset="IP"),
                     ], split_by_field="src")
    # The following code applies raw instructions to packet (IP src increment).
    # It splits the generated traffic by "ip_src" variable to cores and fix
    # IPv4 header checksum.
    vm2 = STLScVmRaw([STLVmFlowVar(name="src",
                                   min_value=p2_src_start_ip,
                                   max_value=p2_src_end_ip,
                                   size=4, op="inc"),
                      STLVmWrFlowVar(fv_name="src", pkt_offset="IP.src"),
                      STLVmFixIpv4(offset="IP"),
                     ], split_by_field="src")

    return create_streams_v46(base_pkt_a, base_pkt_b, vm1, vm2, frame_size)


def create_streams_v6(traffic_options, frame_size=78):
    """Create two IPv6 packets to be used in stream.

    :param traffic_options: Parameters for packets.
    :param frame_size: Size of L2 frame.
    :type traffic_options: List
    :type frame_size: int
    :return: Packet instances.
    :rtype: Tuple of STLPktBuilder
    """

    if type(frame_size) is int and frame_size < 78:
        print_error("Frame min. size is 78B")
        sys.exit(2)

    p1_src_start_ip = traffic_options['p1_src_start_ip']
    p1_src_end_ip = traffic_options['p1_src_end_ip']
    p1_dst_start_ip = traffic_options['p1_dst_start_ip']
    p2_src_start_ip = traffic_options['p2_src_start_ip']
    p2_src_end_ip = traffic_options['p2_src_end_ip']
    p2_dst_start_ip = traffic_options['p2_dst_start_ip']

    p1_dst_end_ip = traffic_options['p1_dst_end_ip']
    p2_dst_end_ip = traffic_options['p2_dst_end_ip']

    base_pkt_a = Ether()/IPv6(src=p1_src_start_ip, dst=p1_dst_start_ip)
    base_pkt_b = Ether()/IPv6(src=p2_src_start_ip, dst=p2_dst_start_ip)

    # The following code applies raw instructions to packet (IP src/dst
    # increment). It splits the generated traffic by "ip_src"/"ip_dst" variable
    # to cores.
    if p1_dst_end_ip and p2_dst_end_ip:
        base_p1, max_p1 = get_start_end_ipv6(p1_dst_start_ip, p1_dst_end_ip)
        base_p2, max_p2 = get_start_end_ipv6(p2_dst_start_ip, p2_dst_end_ip)

        vm1 = STLScVmRaw([STLVmFlowVar(name="ipv6_dst",
                                       min_value=base_p1,
                                       max_value=max_p1+base_p1,
                                       size=8, op="inc"),
                          STLVmWrFlowVar(fv_name="ipv6_dst",
                                         pkt_offset="IPv6.dst",
                                         offset_fixup=8)
                         ]
                         , split_by_field="ipv6_dst")
        vm2 = STLScVmRaw([STLVmFlowVar(name="ipv6_dst",
                                       min_value=base_p2,
                                       max_value=max_p2+base_p2,
                                       size=8, op="inc"),
                          STLVmWrFlowVar(fv_name="ipv6_dst",
                                         pkt_offset="IPv6.dst",
                                         offset_fixup=8)
                         ]
                         , split_by_field="ipv6_dst")
    else:
        base_p1, max_p1 = get_start_end_ipv6(p1_src_start_ip, p1_src_end_ip)
        base_p2, max_p2 = get_start_end_ipv6(p2_src_start_ip, p2_src_end_ip)

        vm1 = STLScVmRaw([STLVmFlowVar(name="ipv6_src",
                                       min_value=base_p1,
                                       max_value=max_p1+base_p1,
                                       size=8, op="inc"),
                          STLVmWrFlowVar(fv_name="ipv6_src",
                                         pkt_offset="IPv6.src",
                                         offset_fixup=8)
                         ]
                         , split_by_field="ipv6_src")
        vm2 = STLScVmRaw([STLVmFlowVar(name="ipv6_src",
                                       min_value=base_p2,
                                       max_value=max_p2+base_p2,
                                       size=8, op="inc"),
                          STLVmWrFlowVar(fv_name="ipv6_src",
                                         pkt_offset="IPv6.src",
                                         offset_fixup=8)
                         ]
                         , split_by_field="ipv6_src")

    return create_streams_v46(base_pkt_a, base_pkt_b, vm1, vm2, frame_size)

def simple_burst(stream_a, stream_b, stream_lat_a, stream_lat_b, duration, rate,
                 warmup_time, async_start, latency):
    """Run the traffic with specific parameters.

    :param pkt_a: Base packet for stream 1.
    :param pkt_b: Base packet for stream 2.
    :param pkt_lat_a: Base packet for latency stream 1.
    :param pkt_lat_b: Base packet for latency stream 2.
    :param duration: Duration of traffic run in seconds (-1=infinite).
    :param rate: Rate of traffic run [percentage, pps, bps].
    :param warmup_time: Warm up duration.
    :param async_start: Start the traffic and exit.
    :param latency: With latency stats.
    :type pkt_a: STLPktBuilder
    :type pkt_b: STLPktBuilder
    :type pkt_lat_a: STLPktBuilder
    :type pkt_lat_b: STLPktBuilder
    :type duration: int
    :type rate: string
    :type warmup_time: int
    :type async_start: bool
    :type latency: bool
    :return: nothing
    """

    # create client
    client = STLClient()

    total_rcvd = 0
    total_sent = 0
    lost_a = 0
    lost_b = 0
    lat_a = 'NA'
    lat_b = 'NA'

    try:
        # turn this off if too many logs
        #client.set_verbose("high")

        # connect to server
        client.connect()

        # prepare our ports (my machine has 0 <--> 1 with static route)
        client.reset(ports=[0, 1])

        client.add_streams(stream_a, ports=[0])
        client.add_streams(stream_b, ports=[1])

        if latency:
            client.add_streams(stream_lat_a, ports=[0])
            client.add_streams(stream_lat_b, ports=[1])

        #warmup phase
        if warmup_time > 0:
            # clear the stats before injecting
            client.clear_stats()

            # choose rate and start traffic
            client.start(ports=[0, 1], mult=rate, duration=warmup_time)

            # block until done
            client.wait_on_traffic(ports=[0, 1], timeout=(warmup_time+30))

            if client.get_warnings():
                for warning in client.get_warnings():
                    print_error(warning)

            # read the stats after the test
            stats = client.get_stats()

            print "#####warmup statistics#####"
            print json.dumps(stats, indent=4,
                             separators=(',', ': '), sort_keys=True)
            lost_a = stats[0]["opackets"] - stats[1]["ipackets"]
            lost_b = stats[1]["opackets"] - stats[0]["ipackets"]

            print "\npackets lost from 0 --> 1:   {0} pkts".format(lost_a)
            print "packets lost from 1 --> 0:   {0} pkts".format(lost_b)

        # clear the stats before injecting
        client.clear_stats()
        lost_a = 0
        lost_b = 0

        # choose rate and start traffic
        client.start(ports=[0, 1], mult=rate, duration=duration)

        if not async_start:
            # block until done
            client.wait_on_traffic(ports=[0, 1], timeout=(duration+30))

            if client.get_warnings():
                for warning in client.get_warnings():
                    print_error(warning)

            # read the stats after the test
            stats = client.get_stats()

            print "#####statistics#####"
            print json.dumps(stats, indent=4,
                             separators=(',', ': '), sort_keys=True)
            lost_a = stats[0]["opackets"] - stats[1]["ipackets"]
            lost_b = stats[1]["opackets"] - stats[0]["ipackets"]

            if latency:
                lat_a = "/".join((\
                    str(stats["latency"][0]["latency"]["total_min"]),\
                    str(stats["latency"][0]["latency"]["average"]),\
                    str(stats["latency"][0]["latency"]["total_max"])))
                lat_b = "/".join((\
                    str(stats["latency"][1]["latency"]["total_min"]),\
                    str(stats["latency"][1]["latency"]["average"]),\
                    str(stats["latency"][1]["latency"]["total_max"])))

            total_sent = stats[0]["opackets"] + stats[1]["opackets"]
            total_rcvd = stats[0]["ipackets"] + stats[1]["ipackets"]

            print "\npackets lost from 0 --> 1:   {0} pkts".format(lost_a)
            print "packets lost from 1 --> 0:   {0} pkts".format(lost_b)

    except STLError as ex_error:
        print_error(str(ex_error))
        sys.exit(1)

    finally:
        if async_start:
            client.disconnect(stop_traffic=False, release_ports=True)
        else:
            client.disconnect()
            print "rate={0}, totalReceived={1}, totalSent={2}, "\
                "frameLoss={3}, latencyStream0(usec)={4}, "\
                "latencyStream1(usec)={5}".format(rate, total_rcvd,\
                total_sent, lost_a+lost_b, lat_a, lat_b)


def print_error(msg):
    """Print error message on stderr.

    :param msg: Error message to print.
    :type msg: string
    :return: nothing
    """

    sys.stderr.write(msg+'\n')


def parse_args():
    """Parse arguments from cmd line.

    :return: Parsed arguments.
    :rtype ArgumentParser
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--duration", required=True, type=int,
                        help="Duration of traffic run")
    parser.add_argument("-s", "--frame_size", required=True,
                        help="Size of a Frame without padding and IPG")
    parser.add_argument("-r", "--rate", required=True,
                        help="Traffic rate with included units (%, pps)")
    parser.add_argument("-6", "--use_IPv6", action="store_true",
                        default=False,
                        help="Use IPv6 traffic profile instead of IPv4")
    parser.add_argument("--async", action="store_true",
                        default=False,
                        help="Non-blocking call of the script")
    parser.add_argument("--latency", action="store_true",
                        default=False,
                        help="Add latency stream")
    parser.add_argument("-w", "--warmup_time", type=int,
                        default=5,
                        help="Traffic warmup time in seconds, 0 = disable")
#    parser.add_argument("--p1_src_mac",
#                        help="Port 1 source MAC address")
#    parser.add_argument("--p1_dst_mac",
#                        help="Port 1 destination MAC address")
    parser.add_argument("--p1_src_start_ip", required=True,
                        help="Port 1 source start IP address")
    parser.add_argument("--p1_src_end_ip",
                        default=False,
                        help="Port 1 source end IP address")
    parser.add_argument("--p1_dst_start_ip", required=True,
                        help="Port 1 destination start IP address")
    parser.add_argument("--p1_dst_end_ip",
                        default=False,
                        help="Port 1 destination end IP address")
#    parser.add_argument("--p2_src_mac",
#                        help="Port 2 source MAC address")
#    parser.add_argument("--p2_dst_mac",
#                        help="Port 2 destination MAC address")
    parser.add_argument("--p2_src_start_ip", required=True,
                        help="Port 2 source start IP address")
    parser.add_argument("--p2_src_end_ip",
                        default=False,
                        help="Port 2 source end IP address")
    parser.add_argument("--p2_dst_start_ip", required=True,
                        help="Port 2 destination start IP address")
    parser.add_argument("--p2_dst_end_ip",
                        default=False,
                        help="Port 2 destination end IP address")

    return parser.parse_args()


def main():
    """Main function."""

    args = parse_args()

    _duration = args.duration
    _latency = args.latency
    if args.frame_size.isdigit():
        _frame_size = int(args.frame_size)
    else:
        _frame_size = args.frame_size
        _latency = False
    _rate = args.rate
    _use_ipv6 = args.use_IPv6
    _async_call = args.async
    _warmup_time = args.warmup_time

    _traffic_options = {}
    for attr in [a for a in dir(args) if a.startswith('p')]:
        if getattr(args, attr) is not None:
            _traffic_options[attr] = getattr(args, attr)

    if _use_ipv6:
        # WARNING: Trex limitation to IPv4 only. IPv6 is not yet supported.
        print_error('IPv6 latency is not supported yet. Running without lat.')
        _latency = False

        stream_a, stream_b, stream_lat_a, stream_lat_b = create_streams_v6(
            _traffic_options, frame_size=_frame_size)
    else:
        stream_a, stream_b, stream_lat_a, stream_lat_b = create_streams(
            _traffic_options, frame_size=_frame_size)

    simple_burst(stream_a, stream_b, stream_lat_a, stream_lat_b,
                 _duration, _rate, _warmup_time, _async_call, _latency)

if __name__ == "__main__":
    sys.exit(main())
