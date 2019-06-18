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
import argparse
from yaml import load

from resources.libraries.python.ssh import SSH


RESERVATION_DIR = "/tmp/reservation_dir"


def main():
    """Parse arguments, perform the intended action, propagate RC.

    If the intended action is cancellation, reservation dir is deleted.

    If the intended action is reservation, the list is longer:
    1. List contents of reservation dir.
    2. List contents of job.url file in the dir.
    3. Create reservation dir.
    4. Touch file according to -j option.
    5. Put -u option string to file job.url
    From these 5 steps, 1 and 2 are performed always, their RC ignored.
    Steps 3-5 are chained with logical and, any non-zero RC breaks and returns.

    The two files in reservation dir are there for reporting
    which job holds the reservation, so people can manually fix the testbed
    if the job has been aborted, or otherwise failed to unregister.

    The two files have different audiences.
    The URL content is useful if the console is being watched
    from another job web UI. Copy and paste and you see the job run.
    The "tag" as a filename is useful for admins accessing the testbed
    via a graphical terminal, which does not allow copying of text,
    as they need less keypresses to identify the job run.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True,
                        help="Topology file")
    parser.add_argument("-c", "--cancel", help="Cancel reservation",
                        action="store_true")
    parser.add_argument("-j", "--jobtag", required=False, default="Unknown",
                        help="Identifier for Jenkins run suitable as filename")
    parser.add_argument("-u", "--url", required=False, default="Unknown",
                        help="Identifier for Jenkins run suitable as URL")
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
        ret, _, err = ssh.exec_command(
            "ls '{dir}'; head -1 '{dir}/job.url'; mkdir '{dir}' && '
            'touch '{dir}/{jobtag}' && echo '{url}' > '{dir}/job.url'".format(
                dir=RESERVATION_DIR, jobtag=args.jobtag, url=args.url))

    if ret != 0:
        print("{} unsuccessful:\n{}".
              format(("Cancellation " if cancel_reservation else "Reservation"),
                     err))
    return ret


if __name__ == "__main__":
    sys.exit(main())
