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


"""This module implements initialization and cleanup of DPDK environment."""

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class DPDKTools:
    """This class implements:
    - Initialization of DPDK environment,
    - Cleanup of DPDK environment.
    """

    @staticmethod
    def initialize_dpdk_environment(dut_node, dut_if1, dut_if2):
        """
        Initialize the DPDK test environment on the dut_node.
        Load the module uio and igb_uio, then bind the test NIC to the igb_uio.

        :param dut_node: Will init the DPDK on this node.
        :param dut_if1: DUT interface name.
        :param dut_if2: DUT interface name.
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :raises RuntimeError: If it fails to bind the interfaces to igb_uio.
        """
        if dut_node[u"type"] == NodeType.DUT:
            pci_address1 = Topology.get_interface_pci_addr(dut_node, dut_if1)
            pci_address2 = Topology.get_interface_pci_addr(dut_node, dut_if2)
            arch = Topology.get_node_arch(dut_node)

            cmd = f"{Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts" \
                f"/init_dpdk.sh {pci_address1} {pci_address2} {arch}"

            message = (
                u"Failed to bind the interfaces to igb_uio at node"
                f"{dut_node[u'host']}"
            )
            exec_cmd_no_error(
                dut_node, cmd, sudo=True, timeout=600, message=message)

    @staticmethod
    def cleanup_dpdk_environment(dut_node, dut_if1, dut_if2):
        """
        Cleanup the DPDK test environment on the DUT node.
        Unbind the NIC from the igb_uio and bind them to the kernel driver.

        :param dut_node: Will cleanup the DPDK on this node.
        :param dut_if1: DUT interface name.
        :param dut_if2: DUT interface name.
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :raises RuntimeError: If it fails to cleanup the dpdk.
        """
        if dut_node[u"type"] == NodeType.DUT:
            pci_address1 = Topology.get_interface_pci_addr(dut_node, dut_if1)
            if1_driver = Topology.get_interface_driver(dut_node, dut_if1)
            pci_address2 = Topology.get_interface_pci_addr(dut_node, dut_if2)
            if2_driver = Topology.get_interface_driver(dut_node, dut_if2)

            cmd = f"{Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts" \
                f"/cleanup_dpdk.sh {if1_driver} {pci_address1} {if2_driver} " \
                f"{pci_address2}"

            message = f"Failed to cleanup the dpdk at node {dut_node[u'host']}"
            exec_cmd_no_error(
                dut_node, cmd, sudo=True, timeout=1200, message=message)

    @staticmethod
    def install_dpdk_test(node):
        """
        Prepare the DPDK test environment

        :param node: Dictionary created from topology
        :type node: dict
        :returns: nothing
        :raises RuntimeError: If command returns nonzero return code.
        """
        arch = Topology.get_node_arch(node)

        command = f"{Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts" \
            f"/install_dpdk.sh {arch}"
        message = u"Install the DPDK failed!"
        exec_cmd_no_error(node, command, timeout=600, message=message)

        command = f"cat {Constants.REMOTE_FW_DIR}/dpdk*/VERSION"
        message = u"Get DPDK version failed!"
        stdout, _ = exec_cmd_no_error(node, command, message=message)

        logger.info(f"DPDK Version: {stdout}")

    @staticmethod
    def install_dpdk_test_on_all_duts(nodes):
        """
        Prepare the DPDK test environment on all DUTs.

        :param nodes: Nodes from topology file.
        :type nodes: dict
        :returns: nothing
        """
        for node in list(nodes.values()):
            if node[u"type"] == NodeType.DUT:
                DPDKTools.install_dpdk_test(node)
