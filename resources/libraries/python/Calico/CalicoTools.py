# Copyright (c) 2026  Cisco and/or its affiliates.
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

"""
This module deploys Calico framework on node.
"""

from robot.libraries.BuiltIn import BuiltIn
from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology

NB_PORTS = 2


class CalicoTools:
    """Calico utilities."""

    @staticmethod
    def deploy_calico_on_all_duts(nodes, topology_info):
        """
        Deploy calico on all DUJT nodes.

        :param nodes: All the nodes info from the topology file.
        :param topology_info: All the info from the topology file.
        :type nodes: dict
        :type topology_info: dict
        :raises RuntimeError: If bash return code is not 0.
        """
        pass
