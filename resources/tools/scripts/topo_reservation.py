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
from yaml import load

from resources.libraries.python.ssh import SSH


RESERVATION_DIR = "/tmp/reservation_dir"


def diag_cmd(ssh, cmd):
    """Execute cmd, print cmd and stdout, ignore stderr and rc; return None.

    :param ssh: Connected SSH object to execute over.
    :param cmd: Command to execute.
    :type ssh: resources.libraries.python.ssh.SSH
    :type cmd: str
    """
    print "+", cmd
    _, stdout, _ = ssh.exec_command(cmd)
    print stdout


def main():
    """Parse arguments, perform the action, write useful output, propagate RC.

    If the intended action is cancellation, reservation dir is deleted.

    If the intended action is reservation, the list is longer:
    1. List contents of reservation dir.
    2. List contents of test.url file in the dir.
    3. Create reservation dir.
    4. Touch file according to -r option.
    5. Put -u option string to file test.url
    From these 5 steps, 1 and 2 are performed always, their RC ignored.
    RC of step 3 gives the overall result.
    If the result is success, steps 4-5 are executed without any output,
    their RC is ignored.

    The two files in reservation dir are there for reporting
    which test run holds the reservation, so people can manually fix the testbed
    if the rest run has been aborted, or otherwise failed to unregister.

    The two files have different audiences.

    The URL content is useful for people scheduling their test runs
    and wondering why the reservation takes so long.
    For them, a URL (if available) to copy and paste into browser
    to see which test runs are blocking testbeds is the most convenient.

    The "run tag" as a filename is useful for admins accessing the testbed
    via a graphical terminal, which does not allow copying of text,
    as they need less keypresses to identify the test run holding the testbed.
    Also, the listing shows timestamps, which is useful for both audiences.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True,
                        help="Topology file")
    parser.add_argument("-c", "--cancel", help="Cancel reservation",
                        action="store_true")
    parser.add_argument("-r", "--runtag", required=False, default="Unknown",
                        help="Identifier for test run suitable as filename")
    parser.add_argument("-u", "--url", required=False, default="Unknown",
                        help="Identifier for test run suitable as URL")
    args = parser.parse_args()

    work_file = open(args.topo)
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
    if args.cancel:
        ret, _, err = ssh.exec_command("rm -r {}".format(RESERVATION_DIR))
        if ret:
            print "Cancellation unsuccessful:\n{}".format(err)
        return ret
    # Before critical section, output can be outdated already.
    print "Diagnostic commands:"
    diag_cmd(ssh, "ls -l '{dir}'".format(dir=RESERVATION_DIR))
    diag_cmd(ssh, "head -1 '{dir}/run.url'".format(dir=RESERVATION_DIR))
    print "Attempting reservation."
    # Entering critical section.
    ret, _, err = ssh.exec_command("mkdir '{dir}'".format(dir=RESERVATION_DIR))
    # Critical section is over.
    if ret:
        print "Reservation unsuccessful:\n{}".format(err)
        return ret
    # Here the script knows it is the only owner of the testbed.
    print "Success, writing test run info to reservation dir."
    ret2, _, err = ssh.exec_command(
        "touch '{dir}/{runtag}' && ( echo '{url}' > '{dir}/run.url' )".format(
            dir=RESERVATION_DIR, runtag=args.runtag, url=args.url))
    if ret2:
        print "Writing test run info failed, but continuing anyway:\n{}".format(
            err)
    return ret


if __name__ == "__main__":
    sys.exit(main())
