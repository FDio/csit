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

"""Script managing reservation and un-reservation of testbeds.

This script provides simple reservation mechanism to avoid
simultaneous use of nodes listed in topology file.
As source of truth, TG node from the topology file is used.
"""

import sys
sys.exit(0)
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

    # Even if TG is not guaranteed to be a Linux host,
    # we are using it, because testing shows SSH access to DUT
    # during test affects its performance (bursts of lost packets).
    try:
        tg_node = topology["TG"]
    except KeyError:
        print "Topology file does not contain 'TG' node"
        return 1

    ssh = SSH()
    ssh.connect(tg_node)

    # For system reservation we use mkdir it is an atomic operation and we can
    # store additional data (time, client_ID, ..) within reservation directory.
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
