#!/usr/bin/python3

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

sys.path.insert(0, "/opt/trex-core-2.54/scripts/automation/"+\
                   "trex_control_plane/interactive/")
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


if __name__ == "__main__":
    main()
