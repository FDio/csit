#!/usr/bin/python3

# Copyright (c) 2021 Cisco and/or its affiliates.
#
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
#
# Licensed under the Apache License 2.0 or
# GNU General Public License v2.0 or later;  you may not use this file
# except in compliance with one of these Licenses. You
# may obtain a copy of the Licenses at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
#
# Note: If this file is linked with Scapy, which is GPLv2+, your use of it
# must be under GPLv2+.  If at any point in the future it is no longer linked
# with Scapy (or other GPLv2+ licensed software), you are free to choose
# Apache 2.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script uses T-Rex stateless API to drive T-Rex instance.

Requirements:
- T-REX: https://github.com/cisco-system-traffic-generator/trex-core
 - compiled and running T-Rex process (eg. ./t-rex-64 -i)
 - trex.stl.api library
- Script must be executed on a node with T-Rex instance.

Functionality:
1. Verify the API functionality and get server information.
"""

import sys

sys.path.insert(
<<<<<<< HEAD   (ab7c99 PAL: Remove instalation of system dependencies)
    0, u"/opt/trex-core-2.86/scripts/automation/trex_control_plane/interactive/"
=======
    0, u"/opt/trex-core-2.88/scripts/automation/trex_control_plane/interactive/"
>>>>>>> CHANGE (9f35c0 Perf: Bump T-Rex to 2.88)
)
from trex.stl.api import *


def main():
    """Check server info and quit."""
    client = STLClient()
    try:
        # connect to server
        client.connect()

        # get server info
        print(client.get_server_system_info())
    except STLError as ex_error:
        print(ex_error, file=sys.stderr)
        sys.exit(1)
    finally:
        client.disconnect()


if __name__ == u"__main__":
    main()
