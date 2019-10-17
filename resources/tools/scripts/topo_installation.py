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

from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error, scp_node


def uninstall_package(node, package):
    """If there are packages installed, clean them up.

    :param node: Topology node
    :param package: Package name.
    :type node: dict
    :type package: str
    """
    cmd = ("dpkg -l | grep {package} && "
           "(dpkg --configure -a; "
           "apt-get purge -y '{package}.*'"
            .format(package=package))
    exec_cmd_no_error(node, cmd, sudo=True)


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
    parser.add_argument("-hc", "--honeycomb", help="Include Honeycomb package.",
                        required=False, default=False)

    args = parser.parse_args()
    topology_file = args.topo
    packages = args.packages
    install_dir = args.directory
    cancel_installation = args.cancel
    honeycomb = args.honeycomb

    with open(topology_file) as work_file:
        topology = load(work_file.read())['nodes']

    for node in topology:
        if topology[node]['type'] == "DUT":

            if cancel_installation:
                # Remove installation directory on DUT
                cmd = "rm -r {}".format(install_dir)
                exec_cmd(node, cmd)

                if honeycomb:
                    uninstall_package("honeycomb")
                    # remove HC logs
                    cmd = "rm -rf /var/log/honeycomb"
                    exec_cmd(node, cmd, sudo=True)
                uninstall_package("vpp")

            else:
                # Create installation directory on DUT
                cmd = "rm -r {0}; mkdir {0}".format(install_dir)
                exec_cmd(node, cmd)

                need_packages = True
                if honeycomb:
                    cmd = "ls ~/honeycomb | grep .deb"
                    stdout = ssh_ignore_error(ssh, cmd)
                    if "honeycomb" in stdout:
                        # If custom honeycomb packages exist, use them
                        cmd = "cp ~/honeycomb/*.deb {0}".format(install_dir)
                        exec_cmd_no_error(node, cmd)
                        need_packages = False
                if need_packages:
                    # Copy packages from local path to installation dir
                    for deb in packages:
                        scp_node(node, local_path=deb,
                                 remote_path=install_dir)
                if honeycomb:
                    uninstall_package("honeycomb")
                uninstall_package("vpp")

                # Installation of deb packages
                cmd = "dpkg -i --force-all {}/*.deb".format(install_dir)
                exec_cmd_no_error(node, cmd, sudo=True)


if __name__ == "__main__":
    sys.exit(main())
