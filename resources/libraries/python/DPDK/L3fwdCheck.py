# Copyright (c) 2022 Cisco and/or its affiliates.
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

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DpdkUtil import DpdkUtil
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import NodeType, Topology


class L3fwdCheck:
    """Test the DPDK l3fwd is ready."""

    @staticmethod
    def check_l3fwd(node):
        """
        Execute the l3fwd check on the DUT node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If the script "check_l3fwd.sh" fails.
        """
        if node[u"type"] == NodeType.DUT:
            command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
                f"/entry/check_l3fwd.sh"
            message = f"Failed to check l3fwd state at node {node['host']}"
            exec_cmd_no_error(node, command, timeout=1800, message=message)
