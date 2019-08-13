# Copyright (c) 2018 Huawei Technologies Co.,Ltd.
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
from resources.libraries.python.DMM.DMMConstants import DMMConstants as con
from resources.libraries.python.topology import NodeType, Topology

__all__ = ["SetupDMMTest"]


class SetupDMMTest(SetupFramework):
    """Setup suite run on topology nodes for DMMTest

    Many VAT/CLI based tests need the scripts at remote hosts before executing
    them. This class packs the whole testing directory and copies it over
    to all nodes in topology under /tmp/
    """

    remote_fw_dir = con.REMOTE_FW_DIR
    cmd = 'cd {0} && ./install_prereq.sh {1} 2>&1 | tee log_install_prereq.txt'

    def _needs_tarball(self, node):
        """Return whether node should have tarball prepared in remote_fw_dir.

        :param node: Topology node being set up
        :type node: Topology node
        :returns: The tarball should be recreated on the node
        :rtype: bool
        """
        _ = self
        return node['type'] == NodeType.DUT

    def _needs_virtualenv(self, node):
        """Return whether node should have virtualenv prepared in remote_fw_dir.

        :param node: Topology node being set up
        :type node: Topology node
        :returns: A virtual env should be recreated on the node
        :rtype: bool
        """
        _ = self
        _ = node
        return False

    def _needs_install_command(self, node):
        """Return whether node should have a command executed in remote_fw_dir.

        :param node: Topology node being set up
        :type node: Topology node
        :returns: A command that should be executed on the node
        :rtype: str
        """
        if node['type'] == NodeType.DUT:
            arch = Topology.get_node_arch(node)
            return self.cmd.format(con.DMM_SCRIPTS, arch)
        return None

    @classmethod
    def setup_dmm_test(cls, nodes):
        """Setup framework for DMMTest"""
        return cls.setup_framework(nodes)
