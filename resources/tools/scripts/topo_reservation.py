#!/usr/bin/env python2

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

"""Script managing reservation and un-reservation of testbeds.

This script provides simple reservation mechanism to avoid
simultaneous use of nodes listed in topology file.
As source of truth, TG node from the topology file is used.
"""

import sys
import argparse
import yaml

from resources.libraries.python.ssh import exec_cmd


RESERVATION_DIR = "/tmp/reservation_dir"
RESERVATION_NODE = "TG"


def diag_cmd(node, cmd):
    """Execute cmd, print cmd and stdout, ignore stderr and rc; return None.

    :param node: Node object as parsed from topology file to execute cmd on.
    :param cmd: Command to execute.
    :type ssh: dict
    :type cmd: str
    """
    print('+ {cmd}'.format(cmd=cmd))
    _, stdout, _ = exec_cmd(node, cmd)
    print(stdout)


def main():
    """Parse arguments, perform the action, write useful output, propagate RC.

    If the intended action is cancellation, reservation dir is deleted.

    If the intended action is reservation, the list is longer:
    1. List contents of reservation dir.
    2. List contents of test.url file in the dir.
    3. Create reservation dir.
    4. Touch file according to -r option.
    From these 4 steps, 1 and 2 are performed always, their RC ignored.
    RC of step 3 gives the overall result.
    If the result is success, step 4 is executed without any output,
    their RC is ignored.

    The "run tag" as a filename is useful for admins accessing the testbed
    via a graphical terminal, which does not allow copying of text,
    as they need less keypresses to identify the test run holding the testbed.
    Also, the listing shows timestamps, which is useful for both audiences.

    This all assumes the target system accepts ssh connections.
    If it does not, the caller probably wants to stop trying
    to reserve this system. Therefore this script can return 3 different codes.
    Return code 0 means the reservation was successful.
    Return code 1 means the system is inaccessible (or similarly unsuitable).
    Return code 2 means the system is accessible, but already reserved.
    The reason unsuitable systems return 1 is because that is also the value
    Python returns on encountering and unexcepted exception.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True,
                        help="Topology file")
    parser.add_argument("-c", "--cancel", help="Cancel reservation",
                        action="store_true")
    parser.add_argument("-r", "--runtag", required=False, default="Unknown",
                        help="Identifier for test run suitable as filename")
    args = parser.parse_args()

    with open(args.topo, "r") as topo_file:
        topology = yaml.load(topo_file.read())['nodes']

    # Even if TG is not guaranteed to be a Linux host,
    # we are using it, because testing shows SSH access to DUT
    # during test affects its performance (bursts of lost packets).
    try:
        node = topology[RESERVATION_NODE]
    except KeyError:
        print("Topology file does not contain '{node}' node".
              format(node=RESERVATION_NODE))
        return 1

    # For system reservation we use mkdir it is an atomic operation and we can
    # store additional data (time, client_ID, ..) within reservation directory.
    if args.cancel:
        ret, _, err = exec_cmd(node, "rm -r {dir}".format(dir=RESERVATION_DIR))
        if ret:
            print("Cancellation unsuccessful:\n{err}".format(err=err))
        return ret
    # Before critical section, output can be outdated already.
    print("Diagnostic commands:")
    # -d and * are to supress "total <size>", see https://askubuntu.com/a/61190
    diag_cmd(node, "ls --full-time -ac '{dir}' | tail -n +2".format(
        dir=RESERVATION_DIR))
    print("Attempting testbed reservation.")
    # Entering critical section.
    ret, _, _ = exec_cmd(node, "mkdir '{dir}'".format(dir=RESERVATION_DIR))
    # Critical section is over.
    if ret:
        _, stdo, _ = exec_cmd(node, "ls '{dir}'".format(dir=RESERVATION_DIR))
        print("Testbed already reserved by:\n{stdo}".format(stdo=stdo))
        return 2
    # Here the script knows it is the only owner of the testbed.
    print("Reservation success, writing additional info to reservation dir.")
    ret, _, err = exec_cmd(
        node, "touch '{dir}/{runtag}'"\
        .format(dir=RESERVATION_DIR, runtag=args.runtag))
    if ret:
        print("Writing test run info failed, but continuing anyway:\n{err}".
              format(err=err))
    return 0


if __name__ == "__main__":
    sys.exit(main())
