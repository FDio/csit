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


"""This module implements initialization and cleanup of DPDK framework."""

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
    def initialize_dpdk_framework(node, if1, if2, nic_driver):
        """
        Initialize the DPDK framework on the DUT node.
        Load the module uio and igb_uio, then bind the test NIC to the igb_uio.

        :param node: DUT node.
        :param if1: DUT first interface name.
        :param if2: DUT second interface name.
        :param nic_driver: Interface driver.
        :type node: dict
        :type if1: str
        :type if2: str
        :type nic_driver: str
        :raises RuntimeError: If it fails to bind the interfaces to driver.
        """
        if node[u"type"] == NodeType.DUT:
            pci_address1 = Topology.get_interface_pci_addr(node, if1)
            pci_address2 = Topology.get_interface_pci_addr(node, if2)

            command = f"{Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts" \
                f"/init_dpdk.sh {nic_driver} {pci_address1} {pci_address2}"
            message = u"Initialize the DPDK failed!"
            exec_cmd_no_error(node, command, timeout=600, message=message)

    @staticmethod
    def cleanup_dpdk_framework(node, if1, if2):
        """
        Cleanup the DPDK framework on the DUT node.
        Unbind the NIC from the igb_uio and bind them to the kernel driver.

        :param node: Will cleanup the DPDK on this node.
        :param if1: DUT first interface name.
        :param if2: DUT second interface name.
        :type node: dict
        :type if1: str
        :type if2: str
        :raises RuntimeError: If it fails to cleanup the dpdk.
        """
        if node[u"type"] == NodeType.DUT:
            pci_address1 = Topology.get_interface_pci_addr(node, if1)
            pci_address2 = Topology.get_interface_pci_addr(node, if2)
            # We are not supporting more than one driver
            pci_driver = Topology.get_interface_driver(node, if1)

            command = f"{Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts" \
                f"/cleanup_dpdk.sh {pci_driver} {pci_address1} {pci_address2}"
            message = u"Cleanup the DPDK failed!"
            exec_cmd_no_error(node, command, timeout=1200, message=message)

    @staticmethod
    def install_dpdk_framework(node):
        """
        Prepare the DPDK framework on the DUT node.

        :param node: Node from topology file.
        :type node: dict
        :raises RuntimeError: If command returns nonzero return code.
        """
        command = f"{Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts" \
            f"/install_dpdk.sh"
        message = u"Install the DPDK failed!"
        exec_cmd_no_error(node, command, timeout=600, message=message)

        command = f"cat {Constants.REMOTE_FW_DIR}/dpdk*/VERSION"
        message = u"Get DPDK version failed!"
        stdout, _ = exec_cmd_no_error(node, command, message=message)

        logger.info(f"DPDK Version: {stdout}")

    @staticmethod
    def install_dpdk_framework_on_all_duts(nodes):
        """
        Prepare the DPDK framework on all DUTs.

        :param nodes: Nodes from topology file.
        :type nodes: dict
        """
        for node in list(nodes.values()):
            if node[u"type"] == NodeType.DUT:
                DPDKTools.install_dpdk_framework(node)
