#!/usr/bin/env python3

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

import argparse
import sys
import yaml

from resources.libraries.python.ssh import exec_cmd


RESERVATION_DIR = u"/tmp/reservation_dir"
RESERVATION_NODE = u"TG"


def diagnose(node, res_dir):
    """Run a ls command, print processed output; return None.

    :param node: Node object as parsed from topology file to execute cmd on.
    :param res_dir: Reservation directory to investigate.
    :type ssh: dict
    :type res_dir: str
    """
    command = "ls --full-time -ac -I .. '{res_dir}' | tail -n 1"
    ret, stdout, _ = exec_cmd(node, command)
    # The default Bash does not have "-o pipefail",
    # and tail does not fail on empty string.
    if ret or not stdout:
        print(u"Reservation dir not found, the testbed appears to be free.")
        return
    try:
        _, filename = stdout.rstrip(u"\n").rsplit(u" ", 1)
    except ValueError:
        print(f"ls output is not parseable. More info:")
        print(f"  Command: {command}")
        print(f"  Stdout: {stdout}")
        return
    if filename == u".":
        print(f"Reservation dir present but empty. More info:")
        print(f"  Command: {command}")
        print(f"  Stdout: {stdout}")
        return
    print(f"Testbed appears to be reserved by: {filename}")
    dash_parts = filename.split(u"-")
    if len(dash_parts) < 3:
        return
    if dash_parts[0] != u"jenkins":
        return
    job_name = u"-".join(dash_parts[1:-1])
    run_number = dash_parts[-1]
    print(f"URL: https://jenkins.fd.io/job/{job_name}/{run_number}")


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
    Return code 1 means the system is inaccessible (or similarly unsuitable),
    or invocation of this script failed (e.g. python3 command not found).
    Return code 2 means this script was not found (can happend during refactor).
    Return code 3 means the system is accessible, but already reserved.
    The reason unsuitable systems return 1 is because that is also the value
    Python returns on encountering and unexcepted exception.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(u"-t", u"--topo", required=True, help=u"Topology file")
    parser.add_argument(
        u"-c", u"--cancel", help=u"Cancel reservation", action=u"store_true"
    )
    parser.add_argument(
        u"-r", u"--runtag", required=False, default=u"Unknown",
        help=u"Identifier for test run suitable as filename"
    )
    args = parser.parse_args()

    with open(args.topo, "r") as topo_file:
        topology = yaml.safe_load(topo_file.read())[u"nodes"]

    # Even if TG is not guaranteed to be a Linux host,
    # we are using it, because testing shows SSH access to DUT
    # during test affects its performance (bursts of lost packets).
    try:
        node = topology[RESERVATION_NODE]
    except KeyError:
        print(f"Topology file does not contain '{RESERVATION_NODE}' node")
        return 1

    # For system reservation we use mkdir it is an atomic operation and we can
    # store additional data (time, client_ID, ..) within reservation directory.
    if args.cancel:
        ret, _, err = exec_cmd(node, f"rm -r {RESERVATION_DIR}")
        if ret:
            print(f"Cancellation unsuccessful:\n{err!r}")
        return ret
    # Before critical section, output can be outdated already.
    print(u"Diagnosing the testbed.")
    diagnose(node, RESERVATION_DIR)
    print(u"Attempting testbed reservation.")
    # Entering critical section.
    ret, _, _ = exec_cmd(node, f"mkdir '{RESERVATION_DIR}'")
    # Critical section is over.
    if ret:
        print(u"Testbed already reserved, see the diagnostic output above.")
        return 3
    # Here the script knows it is the only owner of the testbed.
    print(u"Reservation success, writing additional info to reservation dir.")
    ret, _, err = exec_cmd(
        node, f"touch '{RESERVATION_DIR}/{args.runtag}'")
    if ret:
        print(f"Writing test run info failed, but continuing anyway:\n{err!r}")
    return 0


if __name__ == u"__main__":
    sys.exit(main())
