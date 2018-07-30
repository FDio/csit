#!/usr/bin/env python

# Copyright (c) 2018 Cisco and/or its affiliates.
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
import sys
from platform import dist
from yaml import load

from resources.libraries.python.ssh import SSH


def execute_command_ssh(ssh, cmd, sudo=False):
    """Execute a command over ssh channel, and print outputs.

    :param ssh: SSH() object connected to a node.
    :param cmd: Command line to execute on remote node.
    :param sudo: Run command with sudo privilege level..
    :type ssh: SSH() object
    :type cmd: str
    :type sudo: bool
    :returns return_code, stdout, stderr
    :rtype: tuple(int, str, str)
    """
    if sudo:
        ret, stdout, stdout = ssh.exec_command_sudo(cmd, timeout=60)
    else:
        ret, stdout, stdout = ssh.exec_command(cmd, timeout=60)

    print 'return RC {ret}'.format(ret=ret)
    print 'return STDOUT {stdout}'.format(stdout=stdout)
    print 'return STDOUT {stdout}'.format(stdout=stdout)

    return ret, stdout, stdout

def uninstall_package(ssh, package):
    """If there are packages installed, clean them up.

    :param ssh: SSH() object connected to a node.
    :param package: Package name.
    :type ssh: SSH() object
    :type package: str
    """
    if dist()[0] == 'Ubuntu':
        ret, _, _ = ssh.exec_command("dpkg -l | grep {package}".format(
            package=package))
        if ret == 0:
            # Try to fix interrupted installations first.
            execute_command_ssh(ssh, 'dpkg --configure -a', sudo=True)
            # Try to remove installed packages
            execute_command_ssh(ssh, 'apt-get purge -y "{package}.*"'.format(
                package=package), sudo=True)

def kill_process(ssh, process):
    """If there are running processes, kill them.

    :param ssh: SSH() object connected to a node.
    :param process: Process name.
    :type ssh: SSH() object
    :type process: str
    """
    execute_command_ssh(ssh, 'killall -v -s 9 {process}'.format(
        process=process), sudo=True)


def main():
    """Testbed cleanup."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True, help="Topology file")

    args = parser.parse_args()
    topology_file = args.topo

    topology = load(open(topology_file).read())['nodes']

    ssh = SSH()
    for node in topology:
        if topology[node]['type'] == "DUT":
            print "###TI host: {}".format(topology[node]['host'])
            ssh.connect(topology[node])

            # Kill processes.
            kill_process(ssh, 'qemu')
            kill_process(ssh, 'l3fwd')
            kill_process(ssh, 'testpmd')

            # Uninstall packages
            uninstall_package(ssh, 'vpp')
            uninstall_package(ssh, 'honeycomb')

            # Remove HC logs.
            execute_command_ssh(ssh, 'rm -rf /var/log/honeycomb',
                                sudo=True)

            # Kill all containers.
            execute_command_ssh(ssh, 'docker rm $(sudo docker ps -a -q)',
                                sudo=True)

            # Destroy kubernetes.
            execute_command_ssh(ssh, 'kubeadm reset && sudo rm -rf $HOME/.kube',
                                sudo=True)

if __name__ == "__main__":
    sys.exit(main())
