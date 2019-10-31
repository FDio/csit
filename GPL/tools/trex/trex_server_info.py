#!/usr/bin/python3

# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.

"""This script uses T-REX stateless API to drive t-rex instance.

Requirements:
- T-REX: https://github.com/cisco-system-traffic-generator/trex-core
 - compiled and running T-REX process (eg. ./t-rex-64 -i)
 - trex.stl.api library
- Script must be executed on a node with T-REX instance

Functionality:
1. Verify the API functionality and get server information

"""

import sys

sys.path.insert(
    0, u"/opt/trex-core-2.61/scripts/automation/trex_control_plane/interactive/"
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
