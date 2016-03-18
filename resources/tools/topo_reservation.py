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

"""This script provides simple reservation mechanism to avoid
   simultaneous use of nodes listed in topology file.
   As source of truth is used DUT1 node from the topology file."""

import sys
import argparse
from resources.libraries.python.ssh import SSH
from yaml import load

RESERVATION_DIR = "/tmp/reservation_dir"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True,
                        help="Topology file")
    parser.add_argument("-c", "--cancel", help="Cancel reservation",
                        action="store_true")
    args = parser.parse_args()
    topology_file = args.topo
    cancel_reservation = args.cancel

    work_file = open(topology_file)
    topology = load(work_file.read())['nodes']

    #we are using DUT1 node because we expect DUT1 to be a linux host
    #we don't use TG because we don't expect TG to be linux only host
    try:
        tg_node = topology["DUT1"]
    except KeyError:
        print "Topology file does not contain 'DUT1' node"
        return 1

    ssh = SSH()
    ssh.connect(tg_node)

    #For system reservation we use mkdir it is an atomic operation and we can
    #store additional data (time, client_ID, ..) within reservation directory
    if cancel_reservation:
        ret, _, err = ssh.exec_command("rm -r {}".format(RESERVATION_DIR))
    else:
        ret, _, err = ssh.exec_command("mkdir {}".format(RESERVATION_DIR))

    if ret != 0:
        print("{} unsuccessful:\n{}".
              format(("Cancellation " if cancel_reservation else "Reservation"),
                     err))
    return ret

if __name__ == "__main__":
    sys.exit(main())
