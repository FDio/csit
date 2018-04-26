#!/usr/bin/env python2.7
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

"""This executable python module gathers MAC address data from topology nodes.
It requires that all interfaces/port elements in topology have driver field.
This script binds the port in given node to set linux kernel driver and
extracts MAC address from it."""

import sys
import os
import re
from argparse import ArgumentParser

import yaml

from resources.libraries.python.ssh import SSH


def load_topology(args):
    """Load topology file referenced to by parameter passed to this script.

    :param args: Arguments parsed from commandline.
    :type args: ArgumentParser().parse_args()
    :return: Python representation of topology YAML.
    :rtype: dict
    """
    data = None
    with open(args.topology, 'r') as stream:
        try:
            data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print 'Failed to load topology file: {0}'.format(args.topology)
            print exc
            raise

    return data


def ssh_no_error(ssh, cmd):
    """Execute a command over ssh channel, and log and exit if the command
    fails.

    :param ssh: SSH() object connected to a node.
    :param cmd: Command line to execute on remote node.
    :type ssh: SSH() object
    :type cmd: str
    :return: stdout from the SSH command.
    :rtype: str
    """
    ret, stdo, stde = ssh.exec_command(cmd)
    if ret != 0:
        print 'Command execution failed: "{}"'.format(cmd)
        print 'stdout: {0}'.format(stdo)
        print 'stderr: {0}'.format(stde)
        raise RuntimeError('Unexpected ssh command failure')

    return stdo


def update_mac_addresses_for_node(node):
    """For given node loop over all ports with PCI address and look for its MAC
    address.

    This function firstly unbinds the PCI device from its current driver
    and binds it to linux kernel driver. After the device is bound to specific
    linux kernel driver the MAC address is extracted from /sys/bus/pci location
    and stored within the node dictionary that was passed to this function.

    :param node: Node from topology.
    :type node: dict
    """
    for port_name, port in node['interfaces'].items():
        if 'driver' not in port:
            err_msg = '{0} port {1} has no driver element, exiting'.format(
                    node['host'], port_name)
            raise RuntimeError(err_msg)

        ssh = SSH()
        ssh.connect(node)

        # TODO: make following SSH commands into one-liner to save on SSH opers

        # First unbind from current driver
        drvr_dir_path = '/sys/bus/pci/devices/{0}/driver'.format(
                port['pci_address'])
        cmd = '''\
            if [ -d {0} ]; then
                echo {1} | sudo tee {0}/unbind ;
            else
                true Do not have to do anything, port already unbound ;
            fi'''.format(drvr_dir_path, port['pci_address'])
        ssh_no_error(ssh, cmd)

        # Then bind to the 'driver' from topology for given port
        cmd = 'echo {0} | sudo tee /sys/bus/pci/drivers/{1}/bind'.\
              format(port['pci_address'], port['driver'])
        ssh_no_error(ssh, cmd)

        # Then extract the mac address and store it in the topology
        cmd = 'cat /sys/bus/pci/devices/{0}/net/*/address'.format(
                port['pci_address'])
        mac = ssh_no_error(ssh, cmd).strip()
        pattern = re.compile("^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
        if not pattern.match(mac):
            raise RuntimeError('MAC address read from host {0} {1} is in '
                               'bad format "{2}"'
                               .format(node['host'], port['pci_address'], mac))
        print '{0}: Found MAC address of PCI device {1}: {2}'.format(
                node['host'], port['pci_address'], mac)
        port['mac_address'] = mac


def update_nodes_mac_addresses(topology):
    """Loop over nodes in topology and get mac addresses for all listed ports
    based on PCI addresses.

    :param topology: Topology information with nodes.
    :type topology: dict
    """
    for node in topology['nodes'].values():
        update_mac_addresses_for_node(node)


def dump_updated_topology(topology, args):
    """Writes or prints out updated topology file.

    :param topology: Topology information with nodes.
    :param args: Arguments parsed from command line.
    :type topology: dict
    :type args: ArgumentParser().parse_args()
    :return: 1 if error occurred, 0 if successful.
    :rtype: int
    """
    if args.output_file:
        if not args.force:
            if os.path.isfile(args.output_file):
                print ('File {0} already exists. If you want to overwrite this '
                       'file, add -f as a parameter to this script'.format(
                           args.output_file))
                return 1
        with open(args.output_file, 'w') as stream:
            yaml.dump(topology, stream, default_flow_style=False)
    else:
        print yaml.dump(topology, default_flow_style=False)
    return 0


def main():
    """Main function"""
    parser = ArgumentParser()
    parser.add_argument('topology', help="Topology yaml file to read")
    parser.add_argument('--output-file', '-o', help='Output file')
    parser.add_argument('-f', '--force', help='Overwrite existing file',
                        action='store_const', const=True)
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    topology = load_topology(args)
    update_nodes_mac_addresses(topology)
    ret = dump_updated_topology(topology, args)

    return ret


if __name__ == "__main__":
    sys.exit(main())
