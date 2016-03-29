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
from resources.libraries.python.ssh import SSH
from yaml import load

RESERVATION_DIR = "/tmp/reservation_dir/"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True,
                        help="Topology file")
    parser.add_argument("-p", "--packages", required=True, nargs='+',
                        help="Packages paths to copy")
    args = parser.parse_args()
    topology_file = args.topo
    packages = args.packages

    work_file = open(topology_file)
    topology = load(work_file.read())['nodes']

    for node in topology:
        if topology[node]['type'] == "DUT":
            ssh = SSH()
            ssh.connect(topology[node])
            # Copy packages from local path to repository dir
            for deb in packages:
                ssh.scp(local_path=deb,remote_path=RESERVATION_DIR)

            # Installation fo VPP deb packages
            ret, _, err = ssh.exec_command("dpkg -i {}*.deb".format(RESERVATION_DIR))
            if ret != 0:
                print("Installation unsuccessful:\n{}".format(err))
                return ret

if __name__ == "__main__":
    sys.exit(main())
