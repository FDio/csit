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

def main():
    """Copy and installation of VPP packages."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True,
                        help="Topology file")
    parser.add_argument("-d", "--directory", required=True,
                        help="Installation directory")
    parser.add_argument("-p", "--packages", required=True, nargs='*',
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

    for node in topology:
        if topology[node]['type'] == "DUT":
            ssh = SSH()
            ssh.connect(topology[node])

            if cancel_installation:
                ret, _, err = ssh.exec_command("rm -r {}".format(install_dir))
                if ret != 0:
                    print "Cancel unsuccessful:\n{}".format(err)
                    return ret
            else:
                ret, _, err = ssh.exec_command("mkdir {}".format(install_dir))
                if ret != 0:
                    print "Mkdir unsuccessful:\n{}".format(err)
                    return ret

                # Copy packages from local path to installation dir
                for deb in packages:
                    ssh.scp(local_path=deb, remote_path=install_dir)

                # Installation of VPP deb packages
                ret, _, err = ssh.exec_command_sudo(
                    "dpkg -i {}/*.deb".format(install_dir))
                if ret != 0:
                    print "Installation unsuccessful:\n{}".format(err)
                    return ret

if __name__ == "__main__":
    sys.exit(main())
