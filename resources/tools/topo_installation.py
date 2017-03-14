#!/usr/bin/env python

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

"""This script provides copy and installation of VPP build deb packages.
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
    :type ssh: SSH() object
    :type cmd: str
    :return: stdout from the SSH command.
    :rtype: str
    """

    if sudo:
        ret, stdo, stde = ssh.exec_command_sudo(cmd, timeout=60)
    else:
        ret, stdo, stde = ssh.exec_command(cmd, timeout=60)

    if ret != 0:
        print 'Command execution failed: "{}"'.format(cmd)
        print 'stdout: {0}'.format(stdo)
        print 'stderr: {0}'.format(stde)
        raise RuntimeError('Unexpected ssh command failure')

    return stdo


def ssh_ignore_error(ssh, cmd, sudo=False):
    """Execute a command over ssh channel, ignore errors.

    :param ssh: SSH() object connected to a node.
    :param cmd: Command line to execute on remote node.
    :type ssh: SSH() object
    :type cmd: str
    :return: stdout from the SSH command.
    :rtype: str
    """

    if sudo:
        ret, stdo, stde = ssh.exec_command_sudo(cmd)
    else:
        ret, stdo, stde = ssh.exec_command(cmd)

    if ret != 0:
        print 'Command execution failed: "{}"'.format(cmd)
        print 'stdout: {0}'.format(stdo)
        print 'stderr: {0}'.format(stde)

    return stdo


def main():
    """Copy and installation of VPP packages."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True,
                        help="Topology file")
    parser.add_argument("-d", "--directory", required=True,
                        help="Installation directory")
    parser.add_argument("-p", "--packages", required=False, nargs='+',
                        help="Packages paths to copy")
    parser.add_argument("-c", "--cancel", help="Cancel installation",
                        action="store_true")
    args = parser.parse_args()
    topology_file = args.topo
    packages = args.packages
    install_dir = args.directory
    cancel_installation = args.cancel

    work_file = open(topology_file)
    topology = load(work_file.read())['nodes']

    ssh = SSH()
    for node in topology:
        if topology[node]['type'] == "DUT":
            print "###TI host: {}".format(topology[node]['host'])
            ssh.connect(topology[node])

            if cancel_installation:
                # Remove installation directory on DUT
                cmd = "rm -r {}".format(install_dir)
                stdout = ssh_ignore_error(ssh, cmd)
                print "###TI {}".format(stdout)

                cmd = "dpkg -l | grep vpp"
                ret, _, _ = ssh.exec_command(cmd)
                if ret == 0:
                    # Try to fix interrupted installations
                    cmd = 'dpkg --configure -a'
                    stdout = ssh_no_error(ssh, cmd, sudo=True)
                    print "###TI {}".format(stdout)
                    # Try to remove installed vpp.* packages
                    cmd = 'apt-get purge -y "vpp.*"'
                    stdout = ssh_no_error(ssh, cmd, sudo=True)
                    print "###TI {}".format(stdout)
            else:
                # Create installation directory on DUT
                cmd = "rm -r {0}; mkdir {0}".format(install_dir)
                stdout = ssh_no_error(ssh, cmd)
                print "###TI {}".format(stdout)

                # Copy packages from local path to installation dir
                for deb in packages:
                    print "###TI scp: {}".format(deb)
                    ssh.scp(local_path=deb, remote_path=install_dir)

                cmd = "dpkg -l | grep vpp"
                ret, _, _ = ssh.exec_command(cmd)
                if ret == 0:
                    # Try to fix interrupted installations
                    cmd = 'dpkg --configure -a'
                    stdout = ssh_no_error(ssh, cmd, sudo=True)
                    print "###TI {}".format(stdout)
                    # Try to remove installed vpp.* packages
                    cmd = 'apt-get purge -y "vpp.*"'
                    stdout = ssh_no_error(ssh, cmd, sudo=True)
                    print "###TI {}".format(stdout)

                # Installation of VPP deb packages
                cmd = "dpkg -i --force-all {}/*.deb".format(install_dir)
                stdout = ssh_no_error(ssh, cmd, sudo=True)
                print "###TI {}".format(stdout)

if __name__ == "__main__":
    sys.exit(main())
