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

"""This script uses IxNetwork Python API to control IxNetwork.

Requirements:
- IxNetwork v7.51
 - ixnetwork.py library v7.51.1014.17 in /opt/ixnet-7.51

"""

import argparse
import sys
import time

sys.path.insert(0, "/opt/ixnet-7.51/")
from IxNetwork import IxNet


class IxDriverError(Exception):
    """Ixia-driver error handling."""


def add_ports(ixnet, count):
    """Add ports to configuration.

    :param ixnet: Instance of IxNet class.
    :param count: Number of ports to add.
    :type ixnet: IxNet
    :type count: int
    :return: List of ports added to configuration.
    :rtype: list
    """

    if ixnet is None:
        raise ValueError('No Ixnet instance')
    if count <= 0 or count % 2 != 0:
        raise ValueError('Port count must be even and higher then zero')

    for _ in range(count):
        ixnet.add(ixnet.getRoot(), 'vport')

    ixnet.commit()

    return ixnet.getList(ixnet.getRoot(), 'vport')


def configure_endpoints(ixnet, topologies, args):
    """Configure endpoints with topologies.

    :param ixnet: Instance of IxNet class.
    :param topologies: List of topologies.
    :param args: Arguments from command line.
    :type ixnet: IxNet
    :type topologies: list
    :type args: ArgumentParser
    :return: nothing
    """

    if ixnet is None:
        raise ValueError('No Ixnet instance')
    if topologies is None:
        raise ValueError('No topologies found')

    traffic_items = []

    if args.traffic_type == 'ethernetVlan':
        path = '/deviceGroup:1/ethernet:1'
    elif args.traffic_type == 'ipv4':
        path = '/deviceGroup:1/ethernet:1/ipv4:1'
    elif args.traffic_type == 'ipv6':
        path = '/deviceGroup:1/ethernet:1/ipv6:1'
    else:
        raise ValueError('Traffic type not supported')

    # Pairing endpoints and assigning them into traffic items
    for topo1, topo2 in zip(topologies, topologies[1:])[::2]:
        src = [topo1 + path]
        dst = [topo2 + path]
        topo1_name = ixnet.getAttribute(topo1, '-name')
        topo2_name = ixnet.getAttribute(topo2, '-name')
        traffic_item = configure_traffic_item(ixnet, topo1_name, src, dst,
                                              args.frame_size, args.rate,
                                              'pps', args.traffic_type)
        traffic_items.append(traffic_item)
        traffic_item = configure_traffic_item(ixnet, topo2_name, dst, src,
                                              args.frame_size, args.rate,
                                              'pps', args.traffic_type)
        traffic_items.append(traffic_item)

    return traffic_items


def configure_traffic_item(ixnet, name, src_ep, dst_ep, frame_size,
                           rate, rate_type, traffic_type):
    """Create and configure traffic item.

    :param ixnet: Instance of IxNet class.
    :param name: Name of traffic profile.
    :param src_ep: Source topology endpoint.
    :param dst_ep: Destination topology endpoint.
    :param frame_size: L2 frame size.
    :param rate: Rate.
    :param rate_type: Rate type (pps, %, bps).
    :param traffic_type: Traffic type (ipv4, ipv6, ethernet).
    :type ixnet: IxNet
    :type name: str
    :type src_ep: str
    :type dst_ep: str
    :type frame_size: int
    :type rate: str
    :type rate_type: str
    :type traffic_type: str
    :return: Created traffic item string.
    :rtype: str
    """

    if ixnet is None:
        raise ValueError('No Ixnet instance')
    if traffic_type == 'ipv4':
        if frame_size < 64:
            raise ValueError('Min. frame size for traffic type is 64B')
    elif traffic_type == 'ipv6':
        if frame_size < 78:
            raise ValueError('Min. frame size for traffic type is 78B')
    elif traffic_type == 'ethernet':
        pass
    else:
        raise ValueError('Traffic type not supported')

    ixnet.add(ixnet.getRoot() + '/traffic', 'trafficItem')
    ixnet.commit()
    traffic_item = ixnet.getList(ixnet.getRoot() + '/traffic',
                                 'trafficItem')[-1]
    ixnet.setMultiAttribute(traffic_item,
                            '-name', name,
                            '-trafficType', traffic_type,
                            '-allowSelfDestined', False,
                            '-trafficItemType', 'l2L3',
                            '-mergeDestinations', True,
                            '-egressEnabled', False,
                            '-srcDestMesh', 'oneToOne',
                            '-enabled', True,
                            '-routeMesh', 'oneToOne',
                            '-transmitMode', 'interleaved',
                            '-biDirectional', False,
                            '-hostsPerNetwork', 1)
    ixnet.setAttribute(traffic_item, '-trafficType', traffic_type)
    ixnet.add(traffic_item, 'endpointSet',
              '-sources', src_ep,
              '-destinations', dst_ep,
              '-name', 'endpointSet1')
    ixnet.setMultiAttribute(traffic_item + '/configElement:1/frameSize',
                            '-type', 'fixed',
                            '-fixedSize', frame_size)

    if rate_type == 'pps':
        ixnet.setMultiAttribute(traffic_item + '/configElement:1/frameRate',
                                '-type', 'framesPerSecond',
                                '-rate', rate)
    elif rate_type == '%':
        ixnet.setMultiAttribute(traffic_item + '/configElement:1/frameRate',
                                '-type', 'percentLineRate',
                                '-rate', rate)
    elif rate_type == 'bps':
        ixnet.setMultiAttribute(traffic_item + '/configElement:1/frameRate',
                                '-type', 'bitsPerSecond',
                                '-rate', rate)
    else:
        raise ValueError('Rate type not supported')

    ixnet.setMultiAttribute(traffic_item + '/configElement:1/transmissionControl',
                            '-type', 'continuous')
    ixnet.setMultiAttribute(traffic_item + "/tracking",
                            '-trackBy', ['trackingenabled0'])
    ixnet.commit()

    return traffic_item


def configure_protocols(ixnet, vports, args, traffic_opt):
    """Create and configure topologies and protocols.

    :param ixnet: Instance of IxNet class.
    :param vports: List of ports added to configuration.
    :param traffic_opt: Traffic options from command line.
    :type ixnet: IxNet
    :type vports: list
    :type traffic_opt: list
    :return: Topologies list
    :rtype: str
    """

    if ixnet is None:
        raise ValueError('No Ixnet instance')
    if vports is None:
        raise ValueError('Vports is Null')
    if traffic_opt['p1_src_ip_cnt'] != traffic_opt['p2_src_ip_cnt']:
        raise ValueError('Asymmetric flow count')

    topologies = None

    # Add topologies
    for _ in vports:
        ixnet.add(ixnet.getRoot(), 'topology')
    ixnet.commit()

    # Get all topologies
    topologies = ixnet.getList(ixnet.getRoot(), 'topology')

    device_groups = []
    # Pair topology with vport and add device group for each
    for topology, vport in zip(topologies, vports):
        # Add ports to topologies
        ixnet.setAttribute(topology, '-vports', vport)
        # Add device groups to topologies
        ixnet.add(topology, 'deviceGroup')
        ixnet.commit()
        device_groups.append(ixnet.getList(topology, 'deviceGroup')[0])

    ethernets = []
    # Add ethernet protocol stacks to device groups
    for device_group in device_groups:
        ixnet.setAttribute(device_group, '-multiplier',
                           traffic_opt['p1_src_ip_cnt'])
        ixnet.add(device_group, 'ethernet')
        ixnet.commit()
        ethernets.append(ixnet.getList(device_group, 'ethernet')[0])

    for i, ethernet in enumerate(ethernets):
        mac = ixnet.getAttribute(ethernet, '-mac')
        ixnet.setAttribute(mac + '/singleValue', \
            '-value', traffic_opt['p'+str(i+1)+'_src_mac'])

    ipv4s = []
    # Add ipv4 protocol stacks to device groups
    for ethernet in ethernets:
        ixnet.add(ethernet, 'ipv4')
        ixnet.commit()
        ipv4s.append(ixnet.getList(ethernet, 'ipv4')[0])

    ipv6s = []
    # Add ipv6 protocol stacks to device groups
    for ethernet in ethernets:
        ixnet.add(ethernet, 'ipv6')
        ixnet.commit()
        ipv6s.append(ixnet.getList(ethernet, 'ipv6')[0])

    if args.traffic_type == 'ipv4':
        configure_ipv4_protocol(ixnet, ipv4s, traffic_opt)
    elif args.traffic_type == 'ipv6':
        configure_ipv6_protocol(ixnet, ipv6s, traffic_opt)
    else:
        raise ValueError('Traffic type not supported')

    return topologies


def configure_ipv4_protocol(ixnet, ipv4s, traffic_opt):
    """Configure ipv4 protocol.

    :param ixnet: Instance of IxNet class.
    :param ipv4s: List of ipv4 protocols.
    :param traffic_opt: Traffic options from command line.
    :type ixnet: IxNetwork
    :type ipv4s: list
    :type traffic_opt: list
    :return: nothing
    """

    if ixnet is None:
        raise ValueError('No Ixnet instance')

    for i, ipv4 in enumerate(ipv4s):
        address = ixnet.getAttribute(ipv4, '-address')
        gatewayIp = ixnet.getAttribute(ipv4, '-gatewayIp')
        resolveGateway = ixnet.getAttribute(ipv4, '-resolveGateway')
        gatewayMac = ixnet.getAttribute(ipv4, '-manualGatewayMac')

        ixnet.setMultiAttribute(address + '/counter', \
            '-direction', 'increment', \
            '-start', traffic_opt['p'+str(i+1)+'_src_ip'], \
            '-step', '0.0.0.1')
        ixnet.setMultiAttribute(gatewayIp + '/singleValue', \
            '-value', traffic_opt['p'+str(i+1)+'_gw_ip'])
        ixnet.setMultiAttribute(resolveGateway + '/singleValue', \
            '-value', 'false')
        ixnet.setMultiAttribute(gatewayMac + '/singleValue', \
            '-value', traffic_opt['p'+str(i+1)+'_gw_mac'])

    ixnet.commit()


def configure_ipv6_protocol(ixnet, ipv6s, traffic_opt):
    """Configure ipv6 protocol.

    :param ixnet: Instance of IxNet class.
    :param ipv6s: List of ipv6 protocols.
    :param traffic_opt: Traffic options from command line.
    :type ixnet: IxNetwork
    :type ipv6s: list
    :type traffic_opt: list
    :return: nothing
    """

    if ixnet is None:
        raise ValueError('No Ixnet instance')

    for i, ipv6 in enumerate(ipv6s):
        address = ixnet.getAttribute(ipv6, '-address')
        gatewayIp = ixnet.getAttribute(ipv6, '-gatewayIp')
        resolveGateway = ixnet.getAttribute(ipv6, '-resolveGateway')
        gatewayMac = ixnet.getAttribute(ipv6, '-manualGatewayMac')

        ixnet.setMultiAttribute(address + '/counter', \
            '-direction', 'increment', \
            '-start', traffic_opt['p'+str(i+1)+'_src_ip'], \
            '-step', '::1')
        ixnet.setMultiAttribute(gatewayIp + '/singleValue', \
            '-value', traffic_opt['p'+str(i+1)+'_gw_ip'])
        ixnet.setMultiAttribute(resolveGateway + '/singleValue', \
            '-value', 'false')
        ixnet.setMultiAttribute(gatewayMac + '/singleValue', \
            '-value', traffic_opt['p'+str(i+1)+'_gw_mac'])

    ixnet.commit()


def assign_physical_interfaces(ixnet, ixinterfaces):
    """Assign physical interfaces on chassis.

    :param ixnet: Instance of IxNet class.
    :param ixinterfaces: List of physical interfaces (chassis/card/port).
    :type ixnet: IxNet
    :type ixinterfaces: list
    :return: nothing
    """

    vports = ixnet.getList(ixnet.getRoot(), 'vport')
    assign_ifs = ixnet.execute('assignPorts', ixinterfaces, [],
                               ixnet.getList("/", "vport"), True)
    if assign_ifs != vports:
        raise IxDriverError("Assigning ports failed: {}".format(assign_ifs))


def apply_traffic(ixnet, traffic_items):
    """Generate, apply all traffic items.

    :param ixnet: Instance of IxNet class.
    :param traffic_items: List of traffic items.
    :type ixnet: IxNet
    :type traffic_items: list
    :return: nothing
    """

    if ixnet is None:
        raise ValueError('No Ixnet instance')
    if traffic_items is None:
        raise ValueError('No traffic items')

    for traffic_item in traffic_items:
        ixnet.execute('generate', traffic_item)

    ixnet.execute('apply', ixnet.getRoot() + '/traffic')


def start_traffic(ixnet):
    """Start traffic on all traffic items.

    :param ixnet: Instance of IxNet class.
    :type ixnet: IxNet
    :return: nothing
    """

    if ixnet is None:
        raise ValueError('No Ixnet instance')

    ixnet.execute('start', ixnet.getRoot() + '/traffic')


def stop_traffic(ixnet):
    """Stop traffic on all traffic items.

    :param ixnet: Instance of IxNet class.
    :type ixnet: IxNet
    :return: nothing
    """

    if ixnet is None:
        raise ValueError('No Ixnet instance')

    ixnet.execute('stop', ixnet.getRoot() + '/traffic')


def process_statistics(ixnet):
    """Process the statistics.

    :param ixnet: Instance of IxNet class.
    :type ixnet: IxNet
    :return: nothing
    """

    if ixnet is None:
        raise ValueError('No Ixnet instance')

    viewName = "Traffic Item Statistics"
    views = ixnet.getList('/statistics', 'view')
    viewObj = ''
    editedViewName = '::ixNet::OBJ-/statistics/view:\"' + viewName + '\"'
    for view in views:
        if editedViewName == view:
            viewObj = view
            break

    txFrames = ixnet.execute('getColumnValues', viewObj, 'Tx Frames')
    rxFrames = ixnet.execute('getColumnValues', viewObj, 'Rx Frames')

    print txFrames, rxFrames


def print_error(msg):
    """Print error message on stderr.

    :param msg: Error message to print.
    :type msg: string
    :return: nothing
    """

    sys.stderr.write(msg+'\n')


def parse_args():
    """Parse arguments from cmd line.add_ports

    :return: Parsed arguments.
    :rtype ArgumentParser
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ixia_server", required=True,
                        help="IxNetwork TCL server")
    parser.add_argument("-p", "--ixia_port", required=True, type=int,
                        help="IxNetwork TCL port")
    parser.add_argument("-d", "--duration", required=True, type=int,
                        help="Duration of traffic run in seconds")
    parser.add_argument("-s", "--frame_size", required=True, type=int,
                        help="Size of a Frame without padding and IPG")
    parser.add_argument("-r", "--rate", required=True,
                        help="Traffic rate with included units (perc, pps)")
    parser.add_argument("-t", "--traffic_type", required=True,
                        choices=['ipv4', 'ipv6', 'ethernetVlan'],
                        help="Traffic type")
    parser.add_argument("--async", action="store_true",
                        default=False,
                        help="Non-blocking call of the script")
    parser.add_argument("-w", "--warmup_time", type=int,
                        default=0,
                        help="Traffic warmup time in seconds, 0 = disable")
    parser.add_argument("--p1_ix_chassis", required=True,
                        help="Port 1 IXIA Chassis IP address")
    parser.add_argument("--p1_ix_card", required=True, type=int,
                        help="Port 1 IXIA Card")
    parser.add_argument("--p1_ix_port", required=True, type=int,
                        help="Port 1 IXIA Port")
    parser.add_argument("--p1_src_mac", required=True,
                        help="Port 1 source MAC address")
    parser.add_argument("--p1_src_mac_cnt", type=int,
                        default=1,
                        help="Port 1 source MAC address count")
    parser.add_argument("--p1_src_ip", required=True,
                        help="Port 1 source start IP address")
    parser.add_argument("--p1_src_ip_cnt", type=int,
                        default=1,
                        help="Port 1 source IP address count")
    parser.add_argument("--p1_gw_ip", required=True,
                        help="Port 1 gateway IP address")
    parser.add_argument("--p1_gw_mac", required=True,
                        help="Port 1 gateway MAC address")
    parser.add_argument("--p2_ix_chassis", required=True,
                        help="Port 2 IXIA Chassis IP address")
    parser.add_argument("--p2_ix_card", required=True, type=int,
                        help="Port 2 IXIA Card")
    parser.add_argument("--p2_ix_port", required=True, type=int,
                        help="Port 2 IXIA Port")
    parser.add_argument("--p2_src_mac", required=True,
                        help="Port 2 source MAC address")
    parser.add_argument("--p2_src_mac_cnt", type=int,
                        default=1,
                        help="Port 2 source MAC address count")
    parser.add_argument("--p2_src_ip", required=True,
                        help="Port 2 source IP address count")
    parser.add_argument("--p2_src_ip_cnt", type=int,
                        default=1,
                        help="Port 2 source IP address")
    parser.add_argument("--p2_gw_ip", required=True,
                        help="Port 2 gateway IP address")
    parser.add_argument("--p2_gw_mac", required=True,
                        help="Port 2 gateway MAC address")

    return parser.parse_args()


def main():
    """Main function."""

    # Parse comand line arguments
    args = parse_args()
    # Get ixia physical interfaces
    ix_interfaces = [(args.p1_ix_chassis, int(args.p1_ix_card),
                      int(args.p1_ix_port)),
                     (args.p2_ix_chassis, int(args.p2_ix_card),
                      int(args.p2_ix_port)),]
    traffic_options = {}
    for attr in [a for a in dir(args) if a.startswith('p')]:
        if getattr(args, attr) is not None:
            traffic_options[attr] = getattr(args, attr)

    print traffic_options

    try:
        # Create IXIA instance
        ixnet = IxNet()

        # Debuging mode
        ixnet.setDebug(True)

        # Conntect to IxServer
        ixnet.connect(args.ixia_server, '-port', args.ixia_port, '-version',
                      '7.40')

        # Create blank configuration
        ixnet.execute('newConfig')

        # Add interfaces to config
        vports = add_ports(ixnet, len(ix_interfaces))

        # Configure protocols
        topologies = configure_protocols(ixnet, vports, args, traffic_options)

        # Create traffic items
        traffic_items = configure_endpoints(ixnet, topologies, args)

        # Assign physical interfaces on chassis
        assign_physical_interfaces(ixnet, ix_interfaces)

        # Generate and apply traffic
        apply_traffic(ixnet, traffic_items)

        if args.warmup_time > 0:
            # Start traffic
            start_traffic(ixnet)
            # Wait for warmup time
            time.sleep(args.warmup_time)
            # Stop traffic
            stop_traffic(ixnet)
            # Wait for incomming packets
            time.sleep(10)

        # Start traffic
        start_traffic(ixnet)

        if not args.async:
            # Wait for duration time
            time.sleep(args.duration)
            # Stop traffic
            stop_traffic(ixnet)
            # Wait for incomming packets
            time.sleep(10)

            process_statistics(ixnet)
    except Exception as ex_error:
        print_error(str(ex_error))
        sys.exit(1)

    finally:
        ixnet.disconnect()


if __name__ == "__main__":
    sys.exit(main())
