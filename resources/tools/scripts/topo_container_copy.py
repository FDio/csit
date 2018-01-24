#!/usr/bin/env python

# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""This script provides copy and load of Docker container images.
   As destinations are used all DUT nodes from the topology file."""

import sys
import argparse
from yaml import load

from resources.libraries.python.ssh import SSH


def ssh_no_error(ssh, cmd, sudo=False):
    """Execute a command over ssh channel, and log and exit if the command
    fails.

    :param ssh: SSH() object connected to a node.
    :param cmd: Command line to execute on remote node.
    :param sudo: Run command with sudo privileges.
    :type ssh: SSH() object
    :type cmd: str
    :type sudo: bool
    :returns: stdout from the SSH command.
    :rtype: str
    :raises RuntimeError: In case of unexpected ssh command failure
    """
    if sudo:
        ret, stdo, stde = ssh.exec_command_sudo(cmd, timeout=60)
    else:
        ret, stdo, stde = ssh.exec_command(cmd, timeout=60)

    if ret != 0:
        print('Command execution failed: "{}"'.format(cmd))
        print('stdout: {0}'.format(stdo))
        print('stderr: {0}'.format(stde))
        raise RuntimeError('Unexpected ssh command failure')

    return stdo


def ssh_ignore_error(ssh, cmd, sudo=False):
    """Execute a command over ssh channel, ignore errors.

    :param ssh: SSH() object connected to a node.
    :param cmd: Command line to execute on remote node.
    :param sudo: Run command with sudo privileges.
    :type ssh: SSH() object
    :type cmd: str
    :type sudo: bool
    :returns: stdout from the SSH command.
    :rtype: str
    """
    if sudo:
        ret, stdo, stde = ssh.exec_command_sudo(cmd)
    else:
        ret, stdo, stde = ssh.exec_command(cmd)

    if ret != 0:
        print('Command execution failed: "{}"'.format(cmd))
        print('stdout: {0}'.format(stdo))
        print('stderr: {0}'.format(stde))

    return stdo


def main():
    """Copy and load of Docker image."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True,
                        help="Topology file")
    parser.add_argument("-d", "--directory", required=True,
                        help="Destination directory")
    parser.add_argument("-i", "--images", required=False, nargs='+',
                        help="Images paths to copy")
    parser.add_argument("-c", "--cancel", help="Cancel all",
                        action="store_true")

    args = parser.parse_args()
    topology_file = args.topo
    images = args.images
    directory = args.directory
    cancel_all = args.cancel

    work_file = open(topology_file)
    topology = load(work_file.read())['nodes']

    ssh = SSH()
    for node in topology:
        if topology[node]['type'] == "DUT":
            print("###TI host: {host}".format(host=topology[node]['host']))
            ssh.connect(topology[node])

            if cancel_all:
                # Remove destination directory on DUT
                cmd = "rm -r {directory}".format(directory=directory)
                stdout = ssh_ignore_error(ssh, cmd)
                print("###TI {stdout}".format(stdout=stdout))

            else:
                # Create installation directory on DUT
                cmd = "rm -r {directory}; mkdir {directory}"\
                    .format(directory=directory)
                stdout = ssh_no_error(ssh, cmd)
                print("###TI {stdout}".format(stdout=stdout))

                # Copy images from local path to destination dir
                for image in images:
                    print("###TI scp: {}".format(image))
                    ssh.scp(local_path=image, remote_path=directory)

                # Load image to Docker.
                cmd = "for f in {directory}/*.tar.gz; do "\
                    "sudo docker load -i $f; done".format(directory=directory)
                stdout = ssh_no_error(ssh, cmd)
                print("###TI {}".format(stdout))

                # Remove <none> images from Docker.
                cmd = "docker rmi $(sudo docker images -f 'dangling=true' -q)"
                stdout = ssh_ignore_error(ssh, cmd, sudo=True)
                print("###TI {}".format(stdout))


if __name__ == "__main__":
    sys.exit(main())
