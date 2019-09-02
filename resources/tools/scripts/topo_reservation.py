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
sys.exit(0)
import argparse
import yaml

from resources.libraries.python.ssh import exec_cmd


RESERVATION_DIR = "/tmp/reservation_dir"


def diag_cmd(node, cmd):
    """Execute cmd, print cmd and stdout, ignore stderr and rc; return None.

    :param node: Node object as parsed from topology file to execute cmd on.
    :param cmd: Command to execute.
    :type ssh: dict
    :type cmd: str
    """
    print "+", cmd
    _, stdout, _ = exec_cmd(node, cmd)
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

    with open(args.topo, "r") as topo_file:
        topology = yaml.load(topo_file.read())['nodes']

    # Even if TG is not guaranteed to be a Linux host,
    # we are using it, because testing shows SSH access to DUT
    # during test affects its performance (bursts of lost packets).
    try:
        tgn = topology["TG"]
    except KeyError:
        print "Topology file does not contain 'TG' node"
        return 1

    # For system reservation we use mkdir it is an atomic operation and we can
    # store additional data (time, client_ID, ..) within reservation directory.
    if args.cancel:
        ret, _, err = exec_cmd(tgn, "rm -r {}".format(RESERVATION_DIR))
        if ret:
            print "Cancellation unsuccessful:\n{}".format(err)
        return ret
    # Before critical section, output can be outdated already.
    print "Diagnostic commands:"
    # -d and * are to supress "total <size>", see https://askubuntu.com/a/61190
    diag_cmd(tgn, "ls --full-time -cd '{dir}'/*".format(dir=RESERVATION_DIR))
    diag_cmd(tgn, "head -1 '{dir}/run.url'".format(dir=RESERVATION_DIR))
    print "Attempting reservation."
    # Entering critical section.
    # TODO: Add optional argument to exec_cmd_no_error to make it
    # sys.exit(ret) instead raising? We do not want to deal with stacktrace.
    ret, _, err = exec_cmd(tgn, "mkdir '{dir}'".format(dir=RESERVATION_DIR))
    # Critical section is over.
    if ret:
        print "Reservation unsuccessful:\n{}".format(err)
        return ret
    # Here the script knows it is the only owner of the testbed.
    print "Success, writing test run info to reservation dir."
    # TODO: Add optional argument to exec_cmd_no_error to print message
    # to console instead raising? We do not want to deal with stacktrace.
    ret2, _, err = exec_cmd(
        tgn, "touch '{dir}/{runtag}' && ( echo '{url}' > '{dir}/run.url' )"\
        .format(dir=RESERVATION_DIR, runtag=args.runtag, url=args.url))
    if ret2:
        print "Writing test run info failed, but continuing anyway:\n{}".format(
            err)
    return ret


if __name__ == "__main__":
    sys.exit(main())
