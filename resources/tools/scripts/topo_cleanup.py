#!/usr/bin/env python

# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""This script provides cleanup routines on all DUTs."""

import argparse
from platform import dist
from yaml import load

from resources.libraries.python.ssh import exec_cmd


def uninstall_package(node, package):
    """If there are packages installed, clean them up.

    :param node: Topology node
    :param package: Package name.
    :type node: dict
    :type package: str
    """
    if dist()[0] == 'Ubuntu':
        cmd = ("dpkg -l | grep {package} && "
               "{{ dpkg --configure -a; "
               "apt-get purge -y '*{package}*' ; }}"
               .format(package=package))
        exec_cmd(node, cmd, sudo=True)


def kill_process(node, process):
    """If there are running processes, kill them.

    :param node: Topology node
    :param process: Process name.
    :type node: dict
    :type process: str
    """
    exec_cmd(node, 'killall -v -s 9 {process}'.format(
        process=process), sudo=True)


def main():
    """Testbed cleanup."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True, help="Topology file")

    args = parser.parse_args()
    topology_file = args.topo

    topology = load(open(topology_file).read())['nodes']

    for node in topology.values():
        if node['type'] == "DUT":
            print "###TI host: {}".format(node['host'])

            # Kill processes.
            kill_process(node, 'qemu')
            kill_process(node, 'l3fwd')
            kill_process(node, 'testpmd')

            # Uninstall packages
            uninstall_package(node, 'vpp')
            uninstall_package(node, 'honeycomb')

            # Remove HC logs.
            exec_cmd(node, 'rm -rf /var/log/honeycomb', sudo=True)

            # Kill all containers.
            exec_cmd(
                node, 'docker ps -q | xargs -r docker rm --force', sudo=True)

            # Destroy kubernetes.
            exec_cmd(node, 'kubeadm reset --force', sudo=True)

            # Remove corefiles leftovers.
            exec_cmd(node, 'rm -f /tmp/*tar.lzo.lrz.xz*', sudo=True)

            # Remove corefiles leftovers.
            exec_cmd(node, 'rm -f /tmp/*core*', sudo=True)

            # Set interfaces in topology down.
            for interface in node['interfaces'].values():
                pci = interface['pci_address']
                exec_cmd(
                    node, "[[ -d {path}/{pci}/net ]] && "
                    "sudo ip link set $(basename {path}/{pci}/net/*) down".
                    format(pci=pci, path='/sys/bus/pci/devices'))


if __name__ == "__main__":
    main()
