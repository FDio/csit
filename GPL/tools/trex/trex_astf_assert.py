#!/usr/bin/python3

# Copyright (c) 2020 Cisco and/or its affiliates.
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

"""This script uses T-Rex advanced stateful (astf) API to drive T-Rex instance.

Requirements:
- T-Rex: https://github.com/cisco-system-traffic-generator/trex-core
 - compiled and running T-Rex process (eg. ./t-rex-64 -i)
 - trex.astf.api library
- Script must be executed on a node with T-Rex instance.

Functionality:
1. Verify the API functionality and get server information.
"""

import sys

sys.path.insert(
<<<<<<< HEAD   (180603 Infra: Do not strict check keys in Ansible)
    0, u"/opt/trex-core-2.82/scripts/automation/trex_control_plane/interactive/"
=======
    0, u"/opt/trex-core-2.88/scripts/automation/trex_control_plane/interactive/"
>>>>>>> CHANGE (aadd20 Perf: Bump T-Rex to 2.88)
)
from trex.astf.api import *


def main():
    """Check server info and quit."""
    client = ASTFClient()
    try:
        # connect to server
        client.connect()

        # get server info
        print(client.get_server_system_info())
    except TRexError as ex_error:
        print(ex_error, file=sys.stderr)
        sys.exit(1)
    finally:
        client.disconnect()


if __name__ == u"__main__":
    main()
