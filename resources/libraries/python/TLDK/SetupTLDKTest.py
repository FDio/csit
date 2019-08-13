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

from resources.libraries.python.LocalExecution import run
from resources.libraries.python.SetupFramework import SetupFramework
from resources.libraries.python.TLDK.TLDKConstants import TLDKConstants as con
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.TLDK.gen_pcap import gen_all_pcap

__all__ = ["SetupTLDKTest"]


class SetupTLDKTest(SetupFramework):
    """Setup suite run on topology nodes.

    Many VAT/CLI based tests need the scripts at remote hosts before executing
    them. This class packs the whole testing directory and copies it over
    to all nodes in topology under /tmp/
    """

    remote_fw_dir = con.REMOTE_FW_DIR
    cmd = 'cd {0} && ./install_tldk.sh {1}'

    def prepare(self):
        """Prepare for framework setup.

        Download required TLDK and DPDK resources first.
        Base method creates a tarball of current working directory, and stores
        its name in the local_tarball_name attribute.
        The remote_tarball_name attribute is used as the target name on nodes.
        """
        # Remove any previous TLDK and DPDK resources
        run(['rm', '-rf', 'tldk', 'dpdk', con.DPDK_ARCHIVE],
            msg="Could not remove previous TLDK/DPDK resources")

        # Get the latest TLDK and dpdk code.
        run(['git', 'clone', con.TLDK_REPOSITORY],
            msg="Could not clone TLDK repository")
        run(['wget', con.DPDK_ARCHIVE_URL],
            msg="Could not fetch DPDK archive")

        # Generate pcap file used to execute test case.
        gen_all_pcap()
        return super(SetupTLDKTest, self).prepare()

    def _needs_install_command(self, node):
        """Return whether node should have a command executed in remote_fw_dir.

        :param node: Topology node being set up
        :type node: Topology node
        :returns: A command that should be executed on the node
        :rtype: str
        """
        if node['type'] == NodeType.DUT:
            arch = Topology.get_node_arch(node)
            return self.cmd.format(con.TLDK_SCRIPTS, arch)
        return None

    @classmethod
    def setup_tldk_test(cls, nodes):
        """Setup framework for TLDKTest"""
        return cls.setup_framework(nodes)
