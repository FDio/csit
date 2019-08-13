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

"""This module exists to provide setup utilities for the framework on topology
nodes. All tasks required to be run before the actual tests are started is
supposed to end up here.
"""

from resources.libraries.python.SetupFramework import SetupFramework
from resources.libraries.python.topology import NodeType, Topology

__all__ = ["SetupSFCTest"]


class SetupSFCTest(SetupFramework):
    """Setup suite run on topology nodes.

    Many VAT/CLI based tests need the scripts at remote hosts before executing
    them. This class packs the whole testing directory and copies it over
    to all nodes in topology under /tmp/
    """

    cmd = 'cd tests/nsh_sfc/sfc_scripts/ && ./install_sfc.sh {0} {1}'

    def _needs_install_command(self, node):
        """Return whether node should have a command executed in remote_fw_dir.

        :param node: Topology node being set up
        :type node: Topology node
        :returns: A command that should be executed on the node
        :rtype: str
        """
        if node['type'] == NodeType.DUT:
            if_name_list = Topology.get_node_interfaces(node)
            return self.cmd.format(if_name_list[0], if_name_list[1])
        return None

    @classmethod
    def setup_nsh_sfc_test(cls, nodes):
        """Setup framework for DMMTest"""
        return cls.setup_framework(nodes)
